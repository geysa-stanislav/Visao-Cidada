from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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

# --- SEÇÃO DE REPORTES (REFATORADO) ---
class Reporte(models.Model):
    URGENCIA_CHOICES = [('BAIXA', 'Baixa'), ('MEDIA', 'Média'), ('ALTA', 'Alta')]
    # Removido "Denúncia" e "Coleta". Foco apenas em Reporte Informativo.
    TIPO_CHOICES = [('IRREGULARIDADE', 'Reporte de Irregularidade')]
    
    foto = models.ImageField(upload_to='reportes/')
    endereco = models.CharField(max_length=255)
    observacoes = models.TextField(blank=True, null=True)
    # Aumentado o max_length para comportar a palavra 'IRREGULARIDADE'
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='IRREGULARIDADE')
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
    # Adicione no final do models.py

class ColetaESG(models.Model):
    empresa = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Empresa Parceira")
    nome_acao = models.CharField(max_length=200, default="Drive-Thru da Sustentabilidade")
    data_acao = models.DateField(verbose_name="Data da Ação")
    
    # Dados da Planilha que você vai cadastrar manualmente no MVP
    kg_plastico = models.FloatField(default=0, verbose_name="Plástico Arrecadado (kg)")
    kg_vidro = models.FloatField(default=0, verbose_name="Vidro Arrecadado (kg)")
    kg_papel = models.FloatField(default=0, verbose_name="Papel/Papelão Arrecadado (kg)")
    
    # Impacto Ambiental (O que vai brilhar no Dashboard)
    litros_agua_poupada = models.FloatField(default=0, verbose_name="Água Poupada (L)")
    kg_co2_evitado = models.FloatField(default=0, verbose_name="CO2 Evitado (kg)")

    def __str__(self):
        return f"{self.nome_acao} - {self.empresa.username}"
    

class ColetaESG(models.Model):
    empresa = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Empresa Parceira")
    nome_acao = models.CharField(max_length=200, default="Drive-Thru da Sustentabilidade", verbose_name="Nome do Evento/Ação")
    data_acao = models.DateField(verbose_name="Data da Ação", auto_now_add=True)
    data_coleta = models.DateTimeField(default=timezone.now, verbose_name="Data da Ação")
  
    # Entradas (A empresa/você só digita isso)
    kg_plastico = models.FloatField(default=0, verbose_name="Plástico (kg)")
    kg_vidro = models.FloatField(default=0, verbose_name="Vidro (kg)")
    kg_papel = models.FloatField(default=0, verbose_name="Papel/Papelão (kg)")
    kg_metal = models.FloatField(default=0, verbose_name="Metal/Alumínio (kg)")
    kg_organico = models.FloatField(default=0, verbose_name="Orgânico/Compostagem (kg)")
    
    # Saídas (O Sistema calcula e bloqueia)
    litros_agua_poupada = models.FloatField(default=0, verbose_name="Água Poupada (L)")
    kg_co2_evitado = models.FloatField(default=0, verbose_name="CO2 Evitado (kg)")
    analise_ia = models.TextField(blank=True, verbose_name="Laudo Gerado (IA)")

    # A Mágica acontece aqui antes de salvar no banco
  # A Mágica acontece aqui antes de salvar no banco
    def save(self, *args, **kwargs):
        # 1. Fórmulas Padrão ESG
        agua = (self.kg_plastico * 10) + (self.kg_vidro * 2) + (self.kg_papel * 25) + (self.kg_metal * 15)
        co2 = (self.kg_plastico * 1.5) + (self.kg_vidro * 0.3) + (self.kg_papel * 1.7) + (self.kg_metal * 9.0) + (self.kg_organico * 0.5)
        
        self.litros_agua_poupada = agua
        self.kg_co2_evitado = co2
        
        total_kg = self.kg_plastico + self.kg_vidro + self.kg_papel + self.kg_metal + self.kg_organico
        
        # 2. Geração do Texto com a Tag <strong> no nome da empresa
        self.analise_ia = (
            f"Análise Automática: No evento '{self.nome_acao}', foram processados {total_kg}kg de resíduos. "
            f"Através da reciclagem e destinação correta, a <strong>{self.empresa.username}</strong> evitou a emissão de {self.kg_co2_evitado:.1f}kg de CO2 "
            f"na atmosfera e preservou {self.litros_agua_poupada:.1f} litros de água, contribuindo diretamente para as metas ODS 11 e 12."
        )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_acao} - {self.empresa.username}"