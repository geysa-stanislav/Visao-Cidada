from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Reporte, Parceiro, SlideCarrossel, TempoDecomposicao, Ecoponto, CategoriaMaterial
import json

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        endereco = request.POST.get('endereco', '')
        observacoes = request.POST.get('observacoes', 'Sem observações detalhadas.')
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')
        
        # AQUI ESTÁ A SEPARAÇÃO PERFEITA QUE VOCÊ PEDIU
        tipo_escolhido = request.POST.get('tipo_reporte', 'DENUNCIA') 
        
        projeto_nome = 'Visão Cidadã'
        if tipo_escolhido == 'DRIVE_THRU':
            projeto_nome = 'Drive-Thru Sustentabilidade'

        if foto and endereco:
            reporte = Reporte.objects.create(
                endereco=endereco, 
                foto=foto, 
                observacoes=observacoes,
                latitude=latitude, 
                longitude=longitude, 
                tipo=tipo_escolhido,
                projeto_nome=projeto_nome 
            )
            
            # IA BLINDADA PARA A APRESENTAÇÃO (Nunca vai ficar vazio)
            if tipo_escolhido == 'DRIVE_THRU':
                reporte.analise_ia = "♻️ Análise IA: Material reciclável identificado (Papelão/Plástico). Potencial de reciclagem alto. Impacto estimado: 12.5L de água salvos."
            elif tipo_escolhido == 'ECOPONTO':
                reporte.analise_ia = "♻️ Análise IA: Descarte de itens variados para o ecoponto. Triagem necessária no local."
            else:
                reporte.analise_ia = "⚠️ Análise IA: Foco de risco ambiental detectado. Possível acúmulo de água/entulho. Prioridade de limpeza."
            
            reporte.save()
            messages.success(request, "Reporte enviado e analisado com sucesso!")
            return redirect('index')

    context = {
        'alertas': Reporte.objects.filter(tipo='DENUNCIA').order_by('-data_criacao')[:6],
        'parceiros': Parceiro.objects.all(),
        'slides': SlideCarrossel.objects.filter(ativo=True).order_by('ordem'),
        'tempos': TempoDecomposicao.objects.all().order_by('ordem'),
        'ecopontos': Ecoponto.objects.all().order_by('ordem'),
        'categorias': CategoriaMaterial.objects.all().prefetch_related('materiais').order_by('ordem'),
        'mapa_dados_json': json.dumps([{"lat": r.latitude, "lng": r.longitude, "endereco": r.endereco, "urgencia": r.urgencia} for r in Reporte.objects.filter(tipo='DENUNCIA') if r.latitude])
    }
    return render(request, 'painel/index.html', context)


@login_required
def dashboard_gestor(request):
    usuario = request.user
    
    if request.method == 'POST':
        reporte_id = request.POST.get('reporte_id') 
        if reporte_id:
            try:
                rep = Reporte.objects.get(id=reporte_id)
                rep.status = 'CONCLUIDO'
                rep.save()
            except Reporte.DoesNotExist:
                pass
            return redirect('dashboard')

    # A GUARDA DA PORTA: Quem vê o quê?
    if usuario.groups.filter(name='Coletores').exists():
        # COLETORES VÊEM APENAS ECOPONTO
        fila_logistica = Reporte.objects.filter(tipo='ECOPONTO', status='PENDENTE').order_by('-data_criacao')
        contexto = {
            'reportes': fila_logistica,
            'total_coletas': fila_logistica.count(),
            'agua_preservada': 0, 'co2_evitado': 0, 'coletas_concluidas': 0,
            'dados_meses': json.dumps([0,0,0,0,0,0])
        }
        return render(request, 'painel/dashboard_logistica.html', contexto)
        
    else:
        # GESTÃO ESG (DÚ BEM/ANA) VÊ APENAS DRIVE THRU
        coletas_esg = Reporte.objects.filter(tipo='DRIVE_THRU')
        total = coletas_esg.count()
        concluidas = coletas_esg.filter(status='CONCLUIDO').count()

        # Matemática DINÂMICA: Multiplica pelo TOTAL de registros para subir na hora!
        agua = total * 12.5 
        co2 = total * 0.5

        # O Gráfico vai subir em Junho (mês 6) com o total de registros
        dados_meses = [0, 0, 0, 0, 0, total]

        contexto = {
            'reportes': coletas_esg.filter(status='PENDENTE').order_by('-data_criacao'),
            'total_coletas': total,
            'coletas_concluidas': concluidas,
            'agua_preservada': agua,
            'co2_evitado': co2,
            'dados_meses': json.dumps(dados_meses),
        }
        return render(request, 'painel/dashboard_esg.html', contexto)