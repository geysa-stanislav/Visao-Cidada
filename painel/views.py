from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Reporte, Parceiro, SlideCarrossel, TempoDecomposicao, CategoriaMaterial, Material,ColetaESG
from .ia import analisar_reporte
import json
from datetime import datetime

NOMES_CATEGORIA = {
    'LIXO_ACUMULADO': 'Lixo acumulado',
    'DESCARTE_IRREGULAR': 'Descarte irregular',
    'TERRENO_BALDIO': 'Terreno baldio',
    'AGUA_PARADA': 'Água parada',
    'ENTULHO': 'Entulho',
    'QUEIMADA': 'Queimada',
    'OUTRO': 'Outro',
}
# 1. FUNÇÃO AUXILIAR (Definida no topo para ficar disponível para todos)
def get_regiao_simples(lat, lng):
    try:
        lat, lng = float(lat), float(lng)
        if lat > -20.45: return "Norte"
        if lat < -20.50: return "Sul"
        if lng > -54.60: return "Leste"
        if lng < -54.65: return "Oeste"
        return "Centro"
    except: return "Centro"

def calcular_urgencia_dinamica(observacoes, mes):
    observacoes = observacoes.lower()
    urgencia = "BAIXA"
    if mes in [12, 1, 2, 3]:
        if any(p in observacoes for p in ["pneu", "água", "foco", "dengue"]): urgencia = "ALTA"
        elif "lixo" in observacoes: urgencia = "MEDIA"
    elif mes in [7, 8, 9]:
        if any(p in observacoes for p in ["fogo", "queimada", "fumaça"]): urgencia = "ALTA"
        elif "lixo" in observacoes: urgencia = "MEDIA"
    elif any(p in observacoes for p in ["inflamável", "cheiro", "urgente"]): urgencia = "ALTA"
    return urgencia

# 2. VIEWS
def logout_view(request):
    logout(request)
    return redirect('index')
def index(request):
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        endereco = request.POST.get('endereco', '')
        observacoes = request.POST.get('observacoes', 'Sem observações.')
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')
        
        if foto and endereco:
            # Tenta a IA (só lê o texto da descrição). Se falhar, devolve None.
            analise = None
            if observacoes and observacoes != 'Sem observações.':
                analise = analisar_reporte(observacoes, endereco)

            if analise:
                nivel_urgencia = analise['urgencia']
                categoria_legivel = NOMES_CATEGORIA.get(analise['categoria'], 'Outro')
                texto_analise = f"IA ({categoria_legivel}): {analise['orientacao']}"
            else:
                # Plano B: as regras antigas continuam funcionando
                nivel_urgencia = calcular_urgencia_dinamica(observacoes, datetime.now().month)
                texto_analise = f"Classificação por regras (urgência {nivel_urgencia}), com base em palavras-chave e época do ano."

            reporte = Reporte.objects.create(
                endereco=endereco, foto=foto, observacoes=observacoes,
                latitude=latitude, longitude=longitude, tipo='IRREGULARIDADE',
                urgencia=nivel_urgencia, projeto_nome='Visão Cidadã',
                analise_ia=texto_analise
            )
            if analise and analise['orientacao']:
                messages.success(request, f"Reporte enviado! Orientação da IA: {analise['orientacao']}")
            else:
                messages.success(request, "Reporte enviado!")
            return redirect('index')

    # 1. Definimos a variável ANTES do loop
    alertas = Reporte.objects.filter(tipo='IRREGULARIDADE').order_by('-data_criacao')[:6]
    
    # 2. Executamos o loop de cálculo de região
    for alerta in alertas:
        alerta.regiao = get_regiao_simples(alerta.latitude, alerta.longitude)

    # 3. Geramos os dados do mapa incluindo a região
    mapa_dados = [
        {
            "lat": r.latitude, 
            "lng": r.longitude, 
            "endereco": r.endereco, 
            "urgencia": r.urgencia,
            "regiao": get_regiao_simples(r.latitude, r.longitude)
 } for r in Reporte.objects.filter(tipo='IRREGULARIDADE') if r.latitude
    ]

    # 4. Montamos o contexto limpo
    context = {
        'alertas': alertas,
        'parceiros': Parceiro.objects.all(),
        'slides': SlideCarrossel.objects.filter(ativo=True).order_by('ordem'),
        'tempos': TempoDecomposicao.objects.all().order_by('ordem'),
        'categorias': CategoriaMaterial.objects.all().prefetch_related('materiais').order_by('ordem'),
        'mapa_dados_json': json.dumps(mapa_dados)
    }
    return render(request, 'painel/index.html', context)
@login_required
def dashboard_gestor(request):
    usuario = request.user
    
    # --- 1. AÇÃO COMUM ---
    if request.method == 'POST' and 'reporte_id' in request.POST:
        Reporte.objects.filter(id=request.POST.get('reporte_id')).update(status='CONCLUIDO')
        return redirect('dashboard')

    is_gestao_publica = usuario.groups.filter(name__icontains='Publica').exists() or usuario.groups.filter(name__icontains='Pública').exists()
    
    if is_gestao_publica or usuario.is_superuser:
        # --- LÓGICA DO DASHBOARD LOGÍSTICA (PREFEITURA) ---
        todos_reportes = Reporte.objects.filter(tipo='IRREGULARIDADE')
        fila = todos_reportes.filter(status='PENDENTE').order_by('-data_criacao')
        concluidos = todos_reportes.filter(status='CONCLUIDO')
        
        regioes_contagem = {"Norte": 0, "Sul": 0, "Leste": 0, "Oeste": 0, "Centro": 0}
        urgencia_contagem = {'Alta': 0, 'Média': 0, 'Baixa': 0}
        resolvidos_por_mes = [0] * 12 
        
        for r in todos_reportes:
            regiao = get_regiao_simples(r.latitude, r.longitude)
            regioes_contagem[regiao] += 1
            
            u = {'ALTA': 'Alta', 'MEDIA': 'Média', 'BAIXA': 'Baixa'}.get(r.urgencia, 'Baixa')
            urgencia_contagem[u] += 1
            
            if r.status == 'CONCLUIDO' and r.data_criacao:
                mes_index = r.data_criacao.month - 1
                resolvidos_por_mes[mes_index] += 1

        mapa_dados = []
        for f in fila:
            regiao = get_regiao_simples(f.latitude, f.longitude)
            f.regiao = regiao
            try:
                lat_f, lng_f = float(f.latitude), float(f.longitude)
            except (TypeError, ValueError):
                continue  # reporte sem GPS fica na lista, mas não vai para o mapa
            mapa_dados.append({
                "lat": lat_f + 0.0001,
                "lng": lng_f + 0.0001,
                "regiao": regiao
            })

        regiao_critica = max(regioes_contagem, key=regioes_contagem.get) if any(regioes_contagem.values()) else "Nenhuma"

        contexto = {
            'reportes': fila,
            'total_pendentes': fila.count(),
            'total_concluidos': concluidos.count(),
            'regiao_critica': regiao_critica,
            'mapa_json': json.dumps(mapa_dados),
            'urgencia_json': json.dumps(list(urgencia_contagem.values())),
            'regioes_json': json.dumps(list(regioes_contagem.values())),
            'resolvidos_meses_json': json.dumps(resolvidos_por_mes),
        }
        return render(request, 'painel/dashboard_logistica.html', contexto)
        
    else:
        # --- LÓGICA DO DASHBOARD ESG (EMPRESAS PRIVADA) ---
        from django.db.models import Sum
        from datetime import datetime

        # 1. Se estiver enviando uma nova coleta via formulário
        if request.method == 'POST' and 'litros_agua_poupada' in request.POST:
            # Captura a data do formulário. Se estiver vazio, usa a data de hoje.
            data_str = request.POST.get('data_coleta')
            data_coleta = datetime.strptime(data_str, '%Y-%m-%d') if data_str else datetime.now()
            
            # Aqui você deve criar o objeto usando a data_coleta capturada
            # Certifique-se de que os nomes dos campos batem com seu models.py
            ColetaESG.objects.create(
                empresa=usuario,
                data_coleta=data_coleta,
                litros_agua_poupada=request.POST.get('litros_agua_poupada'),
                kg_co2_evitado=request.POST.get('kg_co2_evitado'),
                kg_plastico=request.POST.get('kg_plastico'),
                kg_vidro=request.POST.get('kg_vidro'),
                kg_papel=request.POST.get('kg_papel'),
                kg_metal=request.POST.get('kg_metal'),
                kg_organico=request.POST.get('kg_organico'),
                nome_acao=request.POST.get('nome_acao')
            )
            return redirect('dashboard') # Recarrega para limpar o POST

        # 2. Lógica de consulta para o Dashboard
        coletas_empresa = ColetaESG.objects.filter(empresa=usuario)
        
        totais = coletas_empresa.aggregate(
            agua=Sum('litros_agua_poupada'),
            co2=Sum('kg_co2_evitado'),
            plastico=Sum('kg_plastico'),
            vidro=Sum('kg_vidro'),
            papel=Sum('kg_papel'),
            metal=Sum('kg_metal'),
            organico=Sum('kg_organico')
        )
        
        # 3. Ações dos últimos 6 meses (para o gráfico)
        NOMES_MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        hoje = datetime.now()
        ano, mes = hoje.year, hoje.month
        meses = []
        for _ in range(6):
            meses.append((ano, mes))
            mes -= 1
            if mes == 0:
                mes, ano = 12, ano - 1
        meses.reverse()
        contagem = {m: 0 for m in meses}
        for c in coletas_empresa:
            if c.data_coleta and (c.data_coleta.year, c.data_coleta.month) in contagem:
                contagem[(c.data_coleta.year, c.data_coleta.month)] += 1
        labels_meses = [NOMES_MESES[m - 1] for (a, m) in meses]
        dados_por_mes = [contagem[m] for m in meses]
        
        ultima_acao = coletas_empresa.order_by('-data_coleta').first()
        texto_ia = ultima_acao.analise_ia if ultima_acao else "Aguardando primeiro evento."

        contexto_esg = {
            'agua_preservada': totais['agua'] or 0,
            'co2_evitado': totais['co2'] or 0,
            'total_coletas': coletas_empresa.count(),
            'dados_meses': json.dumps(dados_por_mes),
            'labels_meses': json.dumps(labels_meses),
            'materiais_json': json.dumps([
                totais['plastico'] or 0, 
                totais['vidro'] or 0, 
                totais['papel'] or 0, 
                totais['metal'] or 0, 
                totais['organico'] or 0
            ]),
            'progresso_agua': min(((totais['agua'] or 0) / 1000) * 100, 100),
            'progresso_co2': min(((totais['co2'] or 0) / 50) * 100, 100),
            'texto_ia': texto_ia,
        }
        return render(request, 'painel/dashboard_esg.html', contexto_esg)