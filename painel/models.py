from django.db import models
from django.contrib.auth.models import User

# --- SEÇÃO DE SLIDES E PARCEIROS ---
class SlideCarrossel(models.Model):
    titulo = models.CharField(max_length=200)
    texto = models.TextField(blank=True, null=True) 
    dado_numerico = models.CharField(max_length=50, blank=True, null=True) 
    icone = models.ImageField(upload_to='carrossel_icones/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    def __str__(self): return self.titulo

class Parceiro(models.Model):
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='parceiros/')
    site_url = models.URLField(blank=True, null=True)
    ordem = models.IntegerField(default=0)
    def __str__(self): return self.nome

# --- SEÇÃO DE INFORMAÇÃO E EDUCAÇÃO ---
class TempoDecomposicao(models.Model):
    material = models.CharField(max_length=100)
    tempo = models.CharField(max_length=100)
    ordem = models.IntegerField(default=0)
    def __str__(self): return self.material

class Ecoponto(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200, default='')
    ordem = models.IntegerField(default=0)
    def __str__(self): return self.nome

# --- NOVA ESTRUTURA DE MATERIAIS (CATEGORIAS) ---
class CategoriaMaterial(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Categoria (ex: Papel, Vidro)")
    ordem = models.IntegerField(default=0)
    def __str__(self): return self.nome

class Material(models.Model):
    categoria = models.ForeignKey(CategoriaMaterial, on_delete=models.CASCADE, related_name='materiais')
    nome = models.CharField(max_length=100)
    is_reciclavel = models.BooleanField(default=True, verbose_name="É reciclável?")
    def __str__(self): return f"{self.nome} ({'Reciclável' if self.is_reciclavel else 'Não'})"

# --- SEÇÃO DE REPORTES ---
class Reporte(models.Model):
    URGENCIA_CHOICES = [('BAIXA', 'Baixa'), ('MEDIA', 'Média'), ('ALTA', 'Alta')]
    TIPO_CHOICES = [('DENUNCIA', 'Foco de Problema'), ('COLETA', 'Descarte/Reciclagem')]
    
    foto = models.ImageField(upload_to='reportes/')
    endereco = models.CharField(max_length=255)
    observacoes = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='DENUNCIA')
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    analise_ia = models.TextField(blank=True, null=True)
    urgencia = models.CharField(max_length=10, choices=URGENCIA_CHOICES, default='BAIXA')
    status = models.CharField(max_length=20, default='PENDENTE')
    data_criacao = models.DateTimeField(auto_now_add=True)
    parceiro = models.ForeignKey(Parceiro, on_delete=models.SET_NULL, null=True, blank=True)
    empresa_dona = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    projeto_nome = models.CharField(max_length=100, default='Visão Cidadã', blank=True, null=True)
    def __str__(self): return f"Reporte em {self.endereco[:30]}"