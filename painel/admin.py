from django.contrib import admin
from .models import Reporte, Parceiro, SlideCarrossel, TempoDecomposicao, CategoriaMaterial, Material, ColetaESG
@admin.register(SlideCarrossel)
class SlideCarrosselAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativo', 'ordem')
    list_editable = ('ativo', 'ordem')

@admin.register(TempoDecomposicao)
class TempoDecomposicaoAdmin(admin.ModelAdmin):
    list_display = ('material', 'tempo', 'ordem')

@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')

@admin.register(CategoriaMaterial)
class CategoriaMaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'is_reciclavel')
    list_filter = ('categoria', 'is_reciclavel')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'endereco', 'urgencia', 'status', 'data_criacao', 'ver_analise_resumida')
    list_filter = ('urgencia', 'status', 'data_criacao')
    search_fields = ('endereco', 'observacoes')
    readonly_fields = ('analise_ia', 'data_criacao')
    
    def ver_analise_resumida(self, obj):
        return obj.analise_ia[:50] + "..." if obj.analise_ia else "Sem análise"
    ver_analise_resumida.short_description = "Resumo IA"

    # No seu painel/admin.py, adicione o ColetaESG no import:

# Coloque isso no final do seu admin.py
class ColetaESGAdmin(admin.ModelAdmin):
    # Trava esses campos para o usuário não conseguir digitar (o sistema calcula sozinho)
    readonly_fields = ('litros_agua_poupada', 'kg_co2_evitado', 'analise_ia')
    # Opcional: Mostra mais colunas na listagem
    list_display = ('nome_acao', 'empresa', 'kg_co2_evitado', 'litros_agua_poupada')

admin.site.register(ColetaESG, ColetaESGAdmin)