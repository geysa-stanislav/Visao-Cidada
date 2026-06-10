from django.contrib import admin
from .models import Reporte, Parceiro, SlideCarrossel, TempoDecomposicao, Ecoponto, CategoriaMaterial, Material

@admin.register(SlideCarrossel)
class SlideCarrosselAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativo', 'ordem')
    list_editable = ('ativo', 'ordem')

@admin.register(TempoDecomposicao)
class TempoDecomposicaoAdmin(admin.ModelAdmin):
    list_display = ('material', 'tempo', 'ordem')

@admin.register(Ecoponto)
class EcopontoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco')

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