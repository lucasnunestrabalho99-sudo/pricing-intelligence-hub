# 📈 PriceOps — Plataforma de Inteligência de Pricing & Revenue Management

> Plataforma analítica de precificação estratégica desenvolvida para distribuidoras e operações de varejo. Cobre desde a engenharia de preços unitária até modelagem econométrica de elasticidade-preço da demanda.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](SEU_LINK_AQUI)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🖼️ Screenshots

### Visão Geral do Portfólio & Curva ABC

<img width="1912" height="918" alt="image" src="https://github.com/user-attachments/assets/92d625ac-beae-4ffd-94ff-92e923a934fc" />

<img width="1899" height="922" alt="image" src="https://github.com/user-attachments/assets/574b5d32-f73f-456b-88b6-f14f17123731" />

### Engenharia de Preços — Price Waterfall

<img width="1920" height="761" alt="image" src="https://github.com/user-attachments/assets/859e2d61-d587-4f1c-9914-b43e30a642dd" />
<img width="1919" height="486" alt="image" src="https://github.com/user-attachments/assets/c32ffcca-4563-49c2-a5ee-f818a7306a6a" />


### Motor de Elasticidade — Painel de Portfólio
<!-- Sugestão: print do painel completo de elasticidades com o gráfico de barras horizontais e a tabela abaixo -->
![Elasticidade](screenshots/elasticidade_portfolio.png)

### Simulador Break-Even Promocional
<!-- Sugestão: print da aba Break-Even com o gráfico de sensibilidade e os KPIs de resultado -->
![Break-Even](screenshots/breakeven.png)

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

Desenvolvido por **Lucas**  
Analista com foco em Inteligência de Pricing, Revenue Management e Otimização de Rentabilidade.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0077B5?logo=linkedin)](linkedin.com/in/lucas-nunes-da-silva-574604216)

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
