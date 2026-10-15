# 🌍 Visão Cidadã - Reporte Cidadão e Gestão ESG

Plataforma desenvolvida durante o **Hackathon Núcleo de Formação Cidadã UFMS**, promovido pelo time **Enactus AGEAD UFMS**. O sistema é um MVP (produto mínimo viável) para mapear descarte irregular de resíduos, orientar o cidadão e apoiar a gestão de impacto ambiental (ESG).

🔗 Site no ar: https://visaocidada.pythonanywhere.com/

## 🚀 O que o sistema faz hoje

- **📍 Reporte do cidadão:** envio de foto, descrição, endereço e GPS. Os reportes aparecem em um mapa de ocorrências de Campo Grande (MS), com nível de urgência.
- **🤖 IA de texto (Groq):** lê a descrição escrita pelo cidadão e sugere uma categoria (por exemplo, água parada, queimada ou entulho), um nível de urgência e uma orientação curta. Se a IA estiver indisponível, o sistema classifica por regras (palavras-chave e época do ano) e o reporte é registrado normalmente.
- **🗂️ Painel de gestão pública (com login):** fila de reportes, confirmação de resolução e gráficos de urgência e de região.
- **📊 Painel ESG (com login):** quantidades coletadas por material nas campanhas de "Drive-Thru" ecológico, com estimativa de CO₂ evitado e de água preservada.
- **♻️ Educação ambiental:** guia visual com resíduo × rejeito, regra do descarte limpo, tempo de decomposição e lista de materiais.

## ⚠️ Limitações atuais

- A IA analisa **apenas o texto** da descrição. Ela não analisa a foto e não faz previsão de ocorrências.
- A classificação da IA é uma sugestão e pode variar entre descrições parecidas.
- Os reportes não são enviados automaticamente à prefeitura: não há integração com órgãos públicos.
- Os fatores de CO₂ e de água são fixos e ainda precisam de fonte e de validação com normas como GRI e SASB.
- Cobertura atual: Campo Grande (MS).

## 💻 Tecnologias Utilizadas

- **Back-end:** Python, Django
- **Front-end:** HTML5, Tailwind CSS, JavaScript, Chart.js, Leaflet
- **Inteligência Artificial:** API da Groq (o modelo é definido por variável de ambiente)
- **Banco de Dados:** SQLite3
- **Hospedagem:** PythonAnywhere

## ▶️ Como rodar no seu computador

```bash
git clone https://github.com/geysa-stanislav/Visao-Cidada.git
cd Visao-Cidada
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install django==5.2.11 pillow groq python-dotenv
```

Crie na raiz do projeto um arquivo `.env` (ele **não** vai para o GitHub):

```
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=nome_de_um_modelo_de_texto_disponivel_na_sua_conta
```

Depois:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sem a chave da Groq, o sistema continua funcionando e usa a classificação por regras.

## 👩‍💻 Autores

- **Geisy Stanislav** (Desenvolvimento & UI/UX)
- **Júnior** (Estratégia & Documentação)

---

*Projeto construído com foco nos Objetivos de Desenvolvimento Sustentável (ODS) da ONU.*