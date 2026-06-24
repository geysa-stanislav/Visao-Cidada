from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Reporte, Parceiro, SlideCarrossel, TempoDecomposicao, CategoriaMaterial, Material,ColetaESG
import json
from datetime import datetime

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
            nivel_urgencia = calcular_urgencia_dinamica(observacoes, datetime.now().month)
            reporte = Reporte.objects.create(
                endereco=endereco, foto=foto, observacoes=observacoes,
                latitude=latitude, longitude=longitude, tipo='IRREGULARIDADE',
                urgencia=nivel_urgencia, projeto_nome='Visão Cidadã' 
            )
            reporte.analise_ia = f"IA: Reporte classificado como {nivel_urgencia} com base na sazonalidade."
            reporte.save()
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
            
            u = r.urgencia.capitalize() if r.urgencia else "Baixa"
            urgencia_contagem[u] = urgencia_contagem.get(u, 0) + 1
            
            if r.status == 'CONCLUIDO' and r.data_criacao:
                mes_index = r.data_criacao.month - 1
                resolvidos_por_mes[mes_index] += 1

        mapa_dados = []
        for f in fila:
            regiao = get_regiao_simples(f.latitude, f.longitude)
            f.regiao = regiao
            mapa_dados.append({
                "lat": float(f.latitude) + 0.0001,
                "lng": float(f.longitude) + 0.0001,
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
        coletas_empresa = ColetaESG.objects.filter(empresa=usuario)
        
        total_agua = sum(c.litros_agua_poupada for c in coletas_empresa)
        total_co2 = sum(c.kg_co2_evitado for c in coletas_empresa)
        
        # Puxando todos os 5 materiais
        total_plastico = sum(c.kg_plastico for c in coletas_empresa)
        total_vidro = sum(c.kg_vidro for c in coletas_empresa)
        total_papel = sum(c.kg_papel for c in coletas_empresa)
        total_metal = sum(c.kg_metal for c in coletas_empresa)
        total_organico = sum(c.kg_organico for c in coletas_empresa)
        
        total_acoes = coletas_empresa.count()
        dados_meses = [0, 0, 0, 0, 0, total_acoes] 
        
        progresso_agua = min((total_agua / 1000) * 100, 100) if total_agua else 0
        progresso_co2 = min((total_co2 / 50) * 100, 100) if total_co2 else 0

        ultima_acao = coletas_empresa.order_by('-id').first()
        texto_ia = ultima_acao.analise_ia if ultima_acao else "Aguardando primeiro evento para gerar análise."

        contexto_esg = {
            'agua_preservada': total_agua,
            'co2_evitado': total_co2,
            'total_coletas': total_acoes,
            'dados_meses': json.dumps(dados_meses),
            # Enviamos os 5 materiais pro HTML
            'materiais_json': json.dumps([total_plastico, total_vidro, total_papel, total_metal, total_organico]),
            'progresso_agua': str(progresso_agua).replace(',', '.'),
            'progresso_co2': str(progresso_co2).replace(',', '.'),
            'texto_ia': texto_ia,
        }
        return render(request, 'painel/dashboard_esg.html', contexto_esg)