# 📈 PriceOps — Plataforma de Inteligência de Pricing & Revenue Management

> Plataforma analítica de precificação estratégica desenvolvida para distribuidoras e operações de varejo. Cobre desde a engenharia de preços unitária até modelagem econométrica de elasticidade-preço da demanda.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pricing-app-nunes.streamlit.app/)

🌐 **Acesse o app ao vivo:** https://pricing-app-nunes.streamlit.app/

---

## 🖼️ Screenshots

### Visão Geral do Portfólio & Curva ABC

<img width="1905" height="437" alt="image" src="https://github.com/user-attachments/assets/8473f9d9-b68d-4e1b-99d3-4560d19136d7" />
<img width="1907" height="748" alt="image" src="https://github.com/user-attachments/assets/4a7fb211-0787-4837-89f1-052b124b9904" />

### Engenharia de Preços — Price Waterfall

<img width="1909" height="423" alt="image" src="https://github.com/user-attachments/assets/202bef96-471c-43ae-94f6-14e4237bef84" />
<img width="1904" height="927" alt="image" src="https://github.com/user-attachments/assets/43ccc7e1-8c32-4e2e-8b61-f63c5da052eb" />
<img width="1907" height="897" alt="image" src="https://github.com/user-attachments/assets/73a4c03e-faa6-4575-8757-c970cc031934" />


### Motor de Elasticidade — Painel de Portfólio
<img width="1906" height="730" alt="image" src="https://github.com/user-attachments/assets/e2185f65-a08e-4f9e-a371-aef10a6d9e3a" />
<img width="1906" height="452" alt="image" src="https://github.com/user-attachments/assets/08fa2ee9-253c-456b-8e2e-d48732ef3ab9" />
<img width="1904" height="906" alt="image" src="https://github.com/user-attachments/assets/0dbaa3c4-d091-4d06-82df-e3f1b8c55f36" />
<img width="1903" height="170" alt="image" src="https://github.com/user-attachments/assets/1084fad8-105c-44b3-a538-1257731ab919" />



### Simulador Break-Even Promocional
<img width="1910" height="527" alt="image" src="https://github.com/user-attachments/assets/cd806872-72f4-402b-83e4-bb147a3c7600" />
<img width="1900" height="487" alt="image" src="https://github.com/user-attachments/assets/2e867a45-3256-4058-9f58-478cbc0e8a38" />

---

## 🎯 Sobre o Projeto

O **PriceOps** nasceu da necessidade de centralizar as principais análises de um analista de pricing em uma única plataforma interativa, acessível e didática. O app permite que qualquer pessoa — do analista ao gestor comercial — entenda o impacto financeiro de cada decisão de preço antes de tomá-la.

O projeto foi construído com foco em **distribuidoras de alimentos**, mas a arquitetura é agnóstica ao setor: qualquer operação com estrutura de custo + imposto + volume pode utilizar a plataforma.

---

## ⚙️ Funcionalidades

### 📦 Módulo 1 — Visão Geral do Portfólio
- Upload de planilha Excel com duas abas (Base Atual + Histórico de Vendas)
- Geração de **base de demonstração** com 12 SKUs reais de uma distribuidora
- KPIs consolidados: SKUs ativos, volume total, receita bruta estimada e margem média
- **Curva ABC interativa** com gráfico de Pareto, classificação A/B/C por faturamento acumulado
- Dispersão **Margem × Volume** (bolhas proporcionais ao faturamento) para identificar estrelas e problemáticos

### 🧮 Módulo 2 — Engenharia de Preços
- **Diagnóstico de Margem:** decomposição unitária em Margem Bruta, Margem de Contribuição e Markup
- **Price Waterfall (Cascata):** visualização das perdas entre o preço de prateleira e o lucro retido
- **Target Margin Seeking:** calcula o preço mínimo necessário para atingir uma margem alvo via Mark-up Divisor (imposto *por dentro*)
- **Break-Even Promocional:** calcula o volume incremental necessário para que um desconto não destrua a massa de margem — com curva de sensibilidade interativa

### 📉 Módulo 3 — Motor de Elasticidade
- **Painel de portfólio completo:** tabela com elasticidade, R², intervalo de confiança 95% e significância estatística para todos os SKUs
- **Gráfico de barras comparativo** com barras de erro e limiar elástico/inelástico
- **Regressão Log-Log (OLS)** para modelagem da curva de demanda histórica
- Alerta automático de qualidade do modelo por faixa de R²
- **Simulador What-If:** projeção de novo preço, volume e faturamento com base na elasticidade calculada
- Evolução temporal de preço e volume sobrepostos

### 📚 Módulo 4 — Hub de Conhecimento
- Glossário técnico integrado: Margem vs. Markup, Elasticidade, R², Curva ABC, Break-Even, Price Waterfall, Efeito Halo e mais
- Fórmulas renderizadas em LaTeX
- Exemplos práticos com valores numéricos

---

## 🚀 Como Executar Localmente

**1. Clone o repositório**
```bash
git clone https://github.com/lucasnunestrabalho99-sudo/pricing-intelligence-hub.git
cd priceops
```

**2. Crie e ative um ambiente virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Execute o app**
```bash
streamlit run priceops_app.py
```

O app estará disponível em `http://localhost:8501`

---

## 📦 Dependências

```txt
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
scipy>=1.11.0
openpyxl>=3.1.0
```

---

## 📊 Formato da Planilha de Entrada

O app aceita arquivos `.xlsx` com **duas abas obrigatórias:**

**Aba 1 — `Base_Atual`**

| SKU | Categoria | Custo_Aquisicao_R$ | Impostos_Percentual | Preco_Atual_R$ | Volume_Mensal_Unid |
|---|---|---|---|---|---|
| Arroz 5kg | Cesta Básica | 18.50 | 0.07 | 23.90 | 1500 |

**Aba 2 — `Historico_Vendas`**

| Data | SKU | Preco_Praticado | Volume_Vendido |
|---|---|---|---|
| 2024-01-01 | Arroz 5kg | 23.90 | 1480 |

> 💡 Baixe a planilha modelo diretamente no Módulo 1 do app.

---

## 🧠 Metodologia

| Análise | Método |
|---|---|
| Elasticidade-Preço | Regressão Log-Log (OLS) — coeficiente angular = elasticidade |
| Formação de Preço | Mark-up Divisor (imposto calculado *por dentro* do preço) |
| Classificação ABC | Princípio de Pareto — 80/95% de faturamento acumulado |
| Break-Even Promocional | `Incremento = %Desconto ÷ (%Margem − %Desconto)` |
| Qualidade do Modelo | R², p-valor e Intervalo de Confiança 95% (scipy.stats) |

---

## 👨‍💻 Autor

Desenvolvido por **Lucas Nunes**  
Economista | Analista com foco em Inteligência de Pricing, Revenue Management e Otimização de Rentabilidade.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0077B5?logo=linkedin)](linkedin.com/in/lucas-nunes-da-silva-574604216)

---
