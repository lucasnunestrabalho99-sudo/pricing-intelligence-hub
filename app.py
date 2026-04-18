import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from scipy import stats

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PriceOps - Revenue Management", layout="wide", page_icon="📈")

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
    .abc-a { background-color: #0d3b2e; color: #00cc96; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .abc-b { background-color: #2d2a0d; color: #ffd700; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .abc-c { background-color: #3b0d0d; color: #ef553b; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .elasticidade-inelastica { color: #00cc96; font-weight: bold; }
    .elasticidade-elastica { color: #ef553b; font-weight: bold; }
    .info-box { background-color: #1a1a2e; border-left: 3px solid #636efa; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES AUXILIARES ---
def formata_br(valor, is_moeda=True, is_percent=False, is_int=False):
    """Formata números para o padrão brasileiro."""
    if is_int:
        return f"{int(valor):,}".replace(",", ".")
    if is_percent:
        return f"{valor:.2f}".replace(".", ",") + "%"
    formato = f"{valor:,.2f}"
    formato = formato.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formato}" if is_moeda else formato


def calcular_elasticidade_produto(df_hist, sku):
    """Calcula elasticidade, R² e intervalo de confiança para um SKU."""
    df_prod = df_hist[df_hist['SKU'] == sku].copy()
    if len(df_prod) < 3:
        return None
    
    # Remover zeros/negativos para o log
    df_prod = df_prod[(df_prod['Preco_Praticado'] > 0) & (df_prod['Volume_Vendido'] > 0)]
    if len(df_prod) < 3:
        return None

    ln_preco = np.log(df_prod['Preco_Praticado'])
    ln_vol = np.log(df_prod['Volume_Vendido'])
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(ln_preco, ln_vol)
    r2 = r_value ** 2
    
    # Intervalo de confiança 95%
    n = len(df_prod)
    t_crit = stats.t.ppf(0.975, df=n - 2)
    ci = t_crit * std_err
    
    return {
        'elasticidade': slope,
        'r2': r2,
        'p_value': p_value,
        'ci_lower': slope - ci,
        'ci_upper': slope + ci,
        'n_obs': n
    }


def classificar_elasticidade(e):
    if e is None:
        return "—"
    if e > -1:
        return "Inelástico"
    elif e <= -1:
        return "Elástico"


def cor_elasticidade(e):
    if e is None:
        return "gray"
    return "#00cc96" if e > -1 else "#ef553b"


def exportar_excel(df_resultado):
    """Gera um arquivo Excel em memória para download."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_resultado.to_excel(writer, sheet_name='Analise_Pricing', index=False)
    return buffer.getvalue()


# --- GERENCIAMENTO DE ESTADO ---
if 'df_dados' not in st.session_state:
    st.session_state['df_dados'] = None
if 'df_historico' not in st.session_state:
    st.session_state['df_historico'] = None


# --- MENU LATERAL ---
st.sidebar.title("Navegação Estratégica")
menu = st.sidebar.radio(
    "Módulos do Sistema:",
    [
        "1. Visão Geral do Portfólio",
        "2. Engenharia de Preços",
        "3. Motor de Elasticidade",
        "4. Hub de Conhecimento"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("PriceOps · Desenvolvido por Lucas · Inteligência de Pricing & Revenue Management")


# =================================================================================
# MÓDULO 1: VISÃO GERAL, IMPORTAÇÃO E CURVA ABC
# =================================================================================
if menu == "1. Visão Geral do Portfólio":
    st.title("📊 Visão Geral e Análise de Portfólio")
    st.markdown("Plataforma de inteligência para gestão de preços, análise de rentabilidade unitária e modelagem preditiva de demanda.")

    col_up, col_btn = st.columns([2, 1])

    with col_up:
        st.markdown("**1. Importe seus dados**")
        arquivo = st.file_uploader("Suba sua base seguindo o padrão do sistema (Apenas Excel .xlsx)", type=["xlsx"])

        with st.expander("Como formatar minha planilha?"):
            st.write("Para habilitar todas as funções (incluindo Elasticidade), baixe nosso modelo. Ele contém duas abas obrigatórias:")
            st.markdown("- **Aba 1 (Base_Atual):** `SKU | Categoria | Custo_Aquisicao_R$ | Impostos_Percentual | Preco_Atual_R$ | Volume_Mensal_Unid`")
            st.markdown("- **Aba 2 (Historico_Vendas):** `Data | SKU | Preco_Praticado | Volume_Vendido`")

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                pd.DataFrame({
                    "SKU": ["Produto Exemplo", "Outro Produto"],
                    "Categoria": ["Cesta Básica", "Bebidas"],
                    "Custo_Aquisicao_R$": [10.00, 4.50],
                    "Impostos_Percentual": [0.15, 0.20],
                    "Preco_Atual_R$": [15.00, 7.90],
                    "Volume_Mensal_Unid": [1000, 3000]
                }).to_excel(writer, sheet_name='Base_Atual', index=False)

                pd.DataFrame({
                    "Data": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-01-01", "2024-02-01", "2024-03-01"],
                    "SKU": ["Produto Exemplo"] * 3 + ["Outro Produto"] * 3,
                    "Preco_Praticado": [15.00, 15.50, 16.00, 7.90, 7.50, 7.00],
                    "Volume_Vendido": [1000, 950, 900, 3000, 3200, 3500]
                }).to_excel(writer, sheet_name='Historico_Vendas', index=False)

            st.download_button(
                label="📥 Baixar Planilha Modelo (Excel 2 Abas)",
                data=buffer.getvalue(),
                file_name="template_priceops.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col_btn:
        st.markdown("**2. Ou explore o ambiente de testes**")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Gerar Base de Demonstração (Cenário Distribuidora)", use_container_width=True):
            dados_teste = pd.DataFrame({
                "SKU": [
                    "Arroz Branco 5kg", "Feijão Preto 1kg", "Óleo de Soja 900ml", "Farinha de Trigo 1kg",
                    "Café Torrado 500g", "Leite UHT Integral 1L", "Queijo Mussarela 1kg", "Iogurte Natural 170g",
                    "Sabão em Pó 1kg", "Amaciante 2L", "Cerveja Pilsen Lata 350ml", "Refrigerante Cola 2L"
                ],
                "Categoria": [
                    "Cesta Básica", "Cesta Básica", "Cesta Básica", "Cesta Básica",
                    "Mercearia", "Laticínios", "Laticínios", "Laticínios",
                    "Limpeza", "Limpeza", "Bebidas", "Bebidas"
                ],
                "Custo_Aquisicao_R$": [18.50, 6.20, 4.80, 3.10, 11.50, 3.80, 28.00, 1.90, 8.50, 7.20, 2.10, 4.50],
                "Impostos_Percentual": [0.07, 0.07, 0.12, 0.07, 0.12, 0.00, 0.12, 0.18, 0.18, 0.18, 0.25, 0.20],
                "Preco_Atual_R$": [23.90, 8.50, 6.50, 4.50, 15.90, 5.50, 39.90, 3.20, 12.90, 10.90, 3.50, 7.90],
                "Volume_Mensal_Unid": [1500, 2200, 3000, 1800, 1200, 4500, 800, 2100, 1600, 1100, 6000, 3500]
            })
            dados_teste['Faturamento_Estimado'] = dados_teste['Preco_Atual_R$'] * dados_teste['Volume_Mensal_Unid']
            st.session_state['df_dados'] = dados_teste

            np.random.seed(42)
            historico = []
            meses = pd.date_range(start="2024-04-01", periods=24, freq="ME")
            elasticidades = {
                "Arroz Branco 5kg": -0.4, "Feijão Preto 1kg": -0.5, "Óleo de Soja 900ml": -0.7,
                "Farinha de Trigo 1kg": -0.6, "Café Torrado 500g": -1.2, "Leite UHT Integral 1L": -0.8,
                "Queijo Mussarela 1kg": -1.5, "Iogurte Natural 170g": -1.3, "Sabão em Pó 1kg": -1.4,
                "Amaciante 2L": -1.6, "Cerveja Pilsen Lata 350ml": -1.8, "Refrigerante Cola 2L": -1.5
            }

            for sku in dados_teste['SKU']:
                preco_base = dados_teste.loc[dados_teste['SKU'] == sku, 'Preco_Atual_R$'].values[0]
                vol_base = dados_teste.loc[dados_teste['SKU'] == sku, 'Volume_Mensal_Unid'].values[0]
                elast = elasticidades[sku]

                for mes in meses:
                    variacao_preco = np.random.uniform(-0.15, 0.15)
                    preco_mes = preco_base * (1 + variacao_preco)
                    ruido_volume = np.random.normal(0, 0.05)
                    variacao_volume = (variacao_preco * elast) + ruido_volume
                    vol_mes = int(vol_base * (1 + variacao_volume))
                    historico.append({
                        "Data": mes, "SKU": sku,
                        "Preco_Praticado": round(preco_mes, 2),
                        "Volume_Vendido": max(10, vol_mes)
                    })

            st.session_state['df_historico'] = pd.DataFrame(historico)
            st.success("Ambiente de demonstração carregado com sucesso!")

    if arquivo is not None:
        try:
            df_base = pd.read_excel(arquivo, sheet_name='Base_Atual')
            df_hist = pd.read_excel(arquivo, sheet_name='Historico_Vendas')
            if 'Faturamento_Estimado' not in df_base.columns:
                df_base['Faturamento_Estimado'] = df_base['Preco_Atual_R$'] * df_base['Volume_Mensal_Unid']
            st.session_state['df_dados'] = df_base
            st.session_state['df_historico'] = df_hist
            st.success("Plataforma alimentada com sucesso! Base Atual e Histórico carregados.")
        except Exception as e:
            st.error(f"Erro na importação. Certifique-se de usar o Template oficial com as duas abas. (Erro: {e})")

    # --- DASHBOARD ---
    if st.session_state['df_dados'] is not None:
        df = st.session_state['df_dados'].copy()

        st.markdown("---")
        st.subheader("Painel de Indicadores (KPIs)")

        fat_total = df['Faturamento_Estimado'].sum()
        vol_total = df['Volume_Mensal_Unid'].sum()
        df['Custo_Total_Imposto'] = df['Custo_Aquisicao_R$'] + (df['Preco_Atual_R$'] * df['Impostos_Percentual'])
        df['Lucro_Bruto'] = df['Preco_Atual_R$'] - df['Custo_Total_Imposto']
        df['Margem_Bruta_Pct'] = (df['Lucro_Bruto'] / df['Preco_Atual_R$']) * 100
        margem_media = (df['Lucro_Bruto'].sum() / df['Preco_Atual_R$'].sum()) * 100

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("SKUs Ativos", len(df))
        kpi2.metric("Volume Total (Unid)", formata_br(vol_total, is_moeda=False, is_int=True))
        kpi3.metric("Receita Bruta Estimada", formata_br(fat_total))
        kpi4.metric("Margem Bruta Média", formata_br(margem_media, is_moeda=False, is_percent=True))

        # --- TABS: PORTFÓLIO + CURVA ABC ---
        tab1, tab2 = st.tabs(["📦 Visão de Portfólio", "🏆 Curva ABC"])

        with tab1:
            col_graf1, col_graf2 = st.columns([2, 1])
            with col_graf1:
                st.write("**Representatividade de Faturamento por Categoria**")
                fat_categoria = df.groupby('Categoria')['Faturamento_Estimado'].sum().reset_index()
                fig_bar = px.bar(
                    fat_categoria.sort_values('Faturamento_Estimado', ascending=True),
                    x='Faturamento_Estimado', y='Categoria', orientation='h',
                    text_auto='.2s', color='Faturamento_Estimado', color_continuous_scale='Teal'
                )
                fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                      showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_graf2:
                st.write("**Dispersão: Margem × Volume**")
                fig_bubble = px.scatter(
                    df, x='Margem_Bruta_Pct', y='Volume_Mensal_Unid',
                    size='Faturamento_Estimado', color='Categoria',
                    hover_name='SKU',
                    labels={'Margem_Bruta_Pct': 'Margem Bruta (%)', 'Volume_Mensal_Unid': 'Volume (Unid)'}
                )
                fig_bubble.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                         margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
                st.plotly_chart(fig_bubble, use_container_width=True)
                st.caption("Bolhas maiores = maior faturamento. Ideal: produtos no quadrante superior direito (alta margem + alto volume).")

        with tab2:
            st.markdown("#### Classificação ABC por Faturamento")
            st.markdown("""
            A Curva ABC segmenta o portfólio pelo princípio de Pareto: os itens **Classe A** representam ~20% dos SKUs 
            mas concentram ~80% do faturamento. São os produtos que não podem faltar no estoque e merecem 
            monitoramento de preço prioritário.
            """)

            df_abc = df[['SKU', 'Categoria', 'Preco_Atual_R$', 'Volume_Mensal_Unid', 'Faturamento_Estimado', 'Margem_Bruta_Pct']].copy()
            df_abc = df_abc.sort_values('Faturamento_Estimado', ascending=False).reset_index(drop=True)
            df_abc['Fat_Acumulado'] = df_abc['Faturamento_Estimado'].cumsum()
            df_abc['Fat_Acumulado_Pct'] = (df_abc['Fat_Acumulado'] / df_abc['Faturamento_Estimado'].sum()) * 100

            def classifica_abc(pct):
                if pct <= 80:
                    return 'A'
                elif pct <= 95:
                    return 'B'
                else:
                    return 'C'

            df_abc['Classe_ABC'] = df_abc['Fat_Acumulado_Pct'].apply(classifica_abc)

            # KPIs por classe
            col_a, col_b, col_c = st.columns(3)
            for classe, col, cor in [('A', col_a, '#00cc96'), ('B', col_b, '#ffd700'), ('C', col_c, '#ef553b')]:
                grupo = df_abc[df_abc['Classe_ABC'] == classe]
                col.metric(
                    f"Classe {classe} — {len(grupo)} SKUs",
                    f"{(grupo['Faturamento_Estimado'].sum() / df_abc['Faturamento_Estimado'].sum() * 100):.1f}% do Fat.",
                    f"{len(grupo)} produto(s)"
                )

            # Gráfico de Pareto
            fig_pareto = go.Figure()
            cores_abc = df_abc['Classe_ABC'].map({'A': '#00cc96', 'B': '#ffd700', 'C': '#ef553b'})
            fig_pareto.add_trace(go.Bar(
                x=df_abc['SKU'], y=df_abc['Faturamento_Estimado'],
                marker_color=cores_abc, name='Faturamento', yaxis='y'
            ))
            fig_pareto.add_trace(go.Scatter(
                x=df_abc['SKU'], y=df_abc['Fat_Acumulado_Pct'],
                mode='lines+markers', name='% Acumulado',
                line=dict(color='#ffffff', width=2), yaxis='y2'
            ))
            fig_pareto.add_hline(y=80, line_dash="dash", line_color="#636efa", annotation_text="80%", yref='y2')
            fig_pareto.add_hline(y=95, line_dash="dash", line_color="#ffd700", annotation_text="95%", yref='y2')
            fig_pareto.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                height=380, margin=dict(l=0, r=0, t=20, b=80),
                yaxis=dict(title='Faturamento (R$)'),
                yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0, 105]),
                xaxis=dict(tickangle=-30),
                legend=dict(orientation='h', y=1.1)
            )
            st.plotly_chart(fig_pareto, use_container_width=True)

            # Tabela ABC
            df_abc_exibe = df_abc.copy()
            df_abc_exibe['Faturamento_Estimado'] = df_abc_exibe['Faturamento_Estimado'].apply(lambda x: formata_br(x))
            df_abc_exibe['Preco_Atual_R$'] = df_abc_exibe['Preco_Atual_R$'].apply(lambda x: formata_br(x))
            df_abc_exibe['Margem_Bruta_Pct'] = df_abc_exibe['Margem_Bruta_Pct'].apply(lambda x: formata_br(x, is_moeda=False, is_percent=True))
            df_abc_exibe['Fat_Acumulado_Pct'] = df_abc_exibe['Fat_Acumulado_Pct'].apply(lambda x: f"{x:.1f}%")
            df_abc_exibe = df_abc_exibe.drop(columns=['Fat_Acumulado', 'Volume_Mensal_Unid'])
            df_abc_exibe.columns = ['SKU', 'Categoria', 'Preço Atual', 'Fat. Estimado', 'Margem Bruta', '% Fat. Acumulado', 'Classe']
            df_abc_exibe.index = df_abc_exibe.index + 1
            st.dataframe(df_abc_exibe, use_container_width=True)

            # Exportação
            df_export = df_abc.copy()
            st.download_button(
                label="📥 Exportar Análise ABC (Excel)",
                data=exportar_excel(df_export),
                file_name="priceops_curva_abc.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# =================================================================================
# MÓDULO 2: ENGENHARIA DE PREÇOS
# =================================================================================
elif menu == "2. Engenharia de Preços":
    st.title("🧮 Engenharia de Preços e Análise de Margem")
    st.markdown("Decomposição do preço de venda (Price Waterfall), Target Margin Seeking e Calculadora de Break-Even Promocional.")

    if st.session_state['df_dados'] is not None:
        skus = st.session_state['df_dados']['SKU'].tolist()
        produto_selecionado = st.selectbox("Selecione o Produto para análise unitária:", skus)
        dados_produto = st.session_state['df_dados'][st.session_state['df_dados']['SKU'] == produto_selecionado].iloc[0]
        custo_base = float(dados_produto['Custo_Aquisicao_R$'])
        imposto_pct = float(dados_produto['Impostos_Percentual']) * 100
        preco_atual = float(dados_produto['Preco_Atual_R$'])
    else:
        st.warning("Carregue os dados no Módulo 1 para habilitar seleções dinâmicas.")
        custo_base, imposto_pct, preco_atual = 10.0, 10.0, 15.0

    st.markdown("---")

    # --- TABS ---
    tab_marg, tab_target, tab_breakeven = st.tabs([
        "📊 Diagnóstico de Margem",
        "🎯 Target Margin Seeking",
        "🔓 Break-Even Promocional"
    ])

    # TAB 1: DIAGNÓSTICO DE MARGEM
    with tab_marg:
        st.subheader("⚙️ Parâmetros Operacionais e Fiscais")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            custo_aquisicao = st.number_input("Custo de Aquisição (R$)", min_value=0.01, value=custo_base, step=0.10, key="ca_marg")
        with col2:
            impostos = st.number_input("Carga Tributária (%)", min_value=0.0, max_value=99.0, value=imposto_pct, step=1.0, key="imp_marg") / 100
        with col3:
            custo_op = st.number_input("Custo Logístico/Fixo (R$)", min_value=0.0, value=1.50, step=0.10, key="cop_marg")
        with col4:
            preco_venda = st.number_input("Preço Praticado na Ponta (R$)", min_value=0.01, value=preco_atual, step=0.50, key="pv_marg")

        valor_impostos = preco_venda * impostos
        custo_total = custo_aquisicao + custo_op + valor_impostos
        lucro_bruto = preco_venda - custo_total
        margem_bruta = (lucro_bruto / preco_venda) * 100 if preco_venda > 0 else 0
        markup = (lucro_bruto / (custo_aquisicao + custo_op)) * 100 if (custo_aquisicao + custo_op) > 0 else 0

        # MC = sem custo fixo (só custo variável de aquisição + impostos)
        margem_contribuicao_pct = ((preco_venda - custo_aquisicao - valor_impostos) / preco_venda) * 100 if preco_venda > 0 else 0

        st.markdown("---")
        st.subheader("📊 Diagnóstico Financeiro Unitário")

        # Delta correto: compara lucro atual vs. cenário sem custo logístico (referência limpa)
        custo_ref = float(dados_produto['Custo_Aquisicao_R$']) if st.session_state['df_dados'] is not None else custo_base
        preco_ref = float(dados_produto['Preco_Atual_R$']) if st.session_state['df_dados'] is not None else preco_atual
        imp_ref = float(dados_produto['Impostos_Percentual']) if st.session_state['df_dados'] is not None else imposto_pct / 100
        lucro_ref = preco_ref - (custo_ref + (preco_ref * imp_ref))
        delta_lucro = lucro_bruto - lucro_ref

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Lucro Bruto Unitário", formata_br(lucro_bruto),
                    delta=f"{formata_br(delta_lucro, is_moeda=False)} vs. base",
                    delta_color="normal" if delta_lucro >= 0 else "inverse")
        kpi2.metric("Margem Bruta (Real)", formata_br(margem_bruta, is_moeda=False, is_percent=True),
                    delta_color="normal" if margem_bruta >= 0 else "inverse")
        kpi3.metric("Margem de Contribuição", formata_br(margem_contribuicao_pct, is_moeda=False, is_percent=True))
        kpi4.metric("Markup sobre Custo", formata_br(markup, is_moeda=False, is_percent=True))

        with st.expander("ℹ️ Diferença entre Margem Bruta e Margem de Contribuição"):
            st.markdown("""
            - **Margem Bruta** considera todos os custos diretos: aquisição + impostos + despesas logísticas/operacionais.
            - **Margem de Contribuição (MC)** considera apenas os custos *variáveis* (aquisição + impostos), excluindo custos fixos rateados. 
            A MC indica quanto cada unidade vendida "contribui" para cobrir os custos fixos da empresa antes de gerar lucro.
            > ⚠️ Precificar olhando apenas a MC sem considerar os custos fixos pode gerar lucro contábil ilusório.
            """)

        st.markdown("### 📉 Cascata de Retenção de Valor (Price Waterfall)")
        fig = go.Figure(go.Waterfall(
            name="Cascata", orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=["Preço de Prateleira", "Tributos", "Custo Aquisição", "Despesas Operacionais", "Lucro Bruto Retido"],
            textposition="outside",
            text=[formata_br(preco_venda), f"-{formata_br(valor_impostos)}", f"-{formata_br(custo_aquisicao)}", f"-{formata_br(custo_op)}", formata_br(lucro_bruto)],
            y=[preco_venda, -valor_impostos, -custo_aquisicao, -custo_op, lucro_bruto],
            connector={"line": {"color": "rgba(255, 255, 255, 0.2)"}},
            decreasing={"marker": {"color": "#ef553b"}},
            increasing={"marker": {"color": "#00cc96"}},
            totals={"marker": {"color": "#636efa" if lucro_bruto >= 0 else "#ef553b"}}
        ))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          height=450, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: TARGET MARGIN
    with tab_target:
        st.subheader("🎯 Otimização de Meta (Target Margin Seeking)")
        st.markdown("Dado um objetivo de Margem Bruta, calcula o **preço mínimo necessário** utilizando o Mark-up Divisor — metodologia que incorpora o imposto *por dentro* do preço.")

        col1, col2, col3 = st.columns(3)
        with col1:
            custo_target = st.number_input("Custo de Aquisição (R$)", min_value=0.01, value=custo_base, step=0.10, key="ca_target")
        with col2:
            impostos_target = st.number_input("Carga Tributária (%)", min_value=0.0, max_value=99.0, value=imposto_pct, step=1.0, key="imp_target") / 100
        with col3:
            custo_op_target = st.number_input("Custo Logístico/Fixo (R$)", min_value=0.0, value=1.50, step=0.10, key="cop_target")

        margem_alvo = st.slider("Meta de Margem Bruta (%)", min_value=1.0, max_value=60.0, value=15.0, step=0.5) / 100

        denominador = 1 - (impostos_target + margem_alvo)
        if denominador > 0:
            preco_sugerido = (custo_target + custo_op_target) / denominador
            markup_result = ((preco_sugerido - custo_target - custo_op_target) / (custo_target + custo_op_target)) * 100

            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("Preço Sugerido (Mark-up Divisor)", formata_br(preco_sugerido))
            col_r2.metric("Markup resultante", formata_br(markup_result, is_moeda=False, is_percent=True))
            col_r3.metric("Margem garantida após impostos", formata_br(margem_alvo * 100, is_moeda=False, is_percent=True))

            st.markdown("""
            <div class="info-box">
            <b>Fórmula do Mark-up Divisor:</b><br>
            <code>Preço = Custos Totais ÷ (1 − %Impostos − %Margem Desejada)</code><br><br>
            Por que não somar o percentual sobre o custo? Porque tributos como ICMS e PIS/COFINS incidem <b>por dentro</b> 
            do preço de venda. Somar markup "por fora" resulta em uma margem real menor do que a planejada.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Combinação de impostos + margem inviável matematicamente (soma ≥ 100%). Revise os parâmetros.")

    # TAB 3: BREAK-EVEN PROMOCIONAL
    with tab_breakeven:
        st.subheader("🔓 Calculadora de Break-Even Promocional")
        st.markdown("""
        Antes de aprovar qualquer desconto, use esta calculadora para responder a pergunta central:
        **"Quanto a mais precisamos vender para que este desconto não destrua nossa margem?"**
        """)

        col1, col2 = st.columns(2)
        with col1:
            margem_atual_be = st.number_input(
                "Margem Bruta atual do produto (%)",
                min_value=1.0, max_value=80.0, value=20.0, step=0.5,
                help="Encontre este valor no diagnóstico de margem ao lado."
            )
        with col2:
            desconto_be = st.number_input(
                "Desconto pretendido (%)",
                min_value=0.5, max_value=float(margem_atual_be - 0.5), value=5.0, step=0.5
            )

        nova_margem_be = margem_atual_be - desconto_be
        denominador_be = margem_atual_be - desconto_be

        if denominador_be > 0:
            incremento_necessario = (desconto_be / denominador_be) * 100

            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("Nova Margem após desconto", formata_br(nova_margem_be, is_moeda=False, is_percent=True),
                          delta=f"-{formata_br(desconto_be, is_moeda=False, is_percent=True)}", delta_color="inverse")
            col_r2.metric("Volume adicional necessário para empatar",
                          formata_br(incremento_necessario, is_moeda=False, is_percent=True))
            col_r3.metric("Resultado sem o volume adicional", "Destruição de Margem 🔴" if incremento_necessario > 20 else "Risco Moderado 🟡")

            # Gráfico de sensibilidade: desconto vs. incremento necessário
            descontos_range = np.arange(1, min(margem_atual_be, 30), 0.5)
            incrementos_range = [(d / (margem_atual_be - d)) * 100 for d in descontos_range if margem_atual_be - d > 0]
            descontos_validos = [d for d in descontos_range if margem_atual_be - d > 0]

            fig_be = go.Figure()
            fig_be.add_trace(go.Scatter(
                x=descontos_validos, y=incrementos_range,
                mode='lines+markers', line=dict(color='#636efa', width=2),
                fill='tozeroy', fillcolor='rgba(99, 110, 250, 0.15)'
            ))
            fig_be.add_vline(x=desconto_be, line_dash="dash", line_color="#ef553b",
                             annotation_text=f"Desconto atual: {desconto_be}%")
            fig_be.update_layout(
                title="Sensibilidade: Desconto × Volume Incremental Necessário",
                xaxis_title="Desconto Concedido (%)",
                yaxis_title="Volume Adicional Necessário para Empatar (%)",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                height=350, margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_be, use_container_width=True)

            st.markdown(f"""
            <div class="info-box">
            Com Margem de <b>{margem_atual_be:.1f}%</b> e desconto de <b>{desconto_be:.1f}%</b>, 
            o time comercial precisa trazer <b>{incremento_necessario:.1f}% a mais em volume</b> 
            para que a empresa apenas <i>empate</i> com a situação atual. 
            Qualquer volume abaixo disso representa redução real da massa de margem.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("O desconto não pode ser igual ou maior que a margem atual.")


# =================================================================================
# MÓDULO 3: MOTOR DE ELASTICIDADE
# =================================================================================
elif menu == "3. Motor de Elasticidade":
    st.title("📉 Econometria e Sensibilidade de Preço")
    st.markdown("Modele a Curva de Demanda histórica via Regressão Log-Log (OLS) e simule o impacto financeiro de estratégias de repasse.")

    has_hist = (
        'df_historico' in st.session_state and
        st.session_state['df_historico'] is not None and
        not st.session_state['df_historico'].empty
    )

    if not has_hist:
        st.warning("⚠️ Dados históricos não identificados. Inicialize o ambiente no Módulo 1.")
        st.stop()

    df_hist_global = st.session_state['df_historico']
    df_base_global = st.session_state['df_dados']
    skus = df_base_global['SKU'].tolist()

    # --- TABELA RESUMO DE ELASTICIDADES (TODOS OS PRODUTOS) ---
    st.subheader("📋 Painel de Elasticidade — Portfólio Completo")
    st.markdown("Visão consolidada da sensibilidade de preço de todos os SKUs. Clique em um produto abaixo para análise individual.")

    resultados_elast = []
    for sku in skus:
        res = calcular_elasticidade_produto(df_hist_global, sku)
        cat = df_base_global.loc[df_base_global['SKU'] == sku, 'Categoria'].values[0]
        if res:
            resultados_elast.append({
                'SKU': sku,
                'Categoria': cat,
                'Elasticidade': res['elasticidade'],
                'R²': res['r2'],
                'IC 95% Inferior': res['ci_lower'],
                'IC 95% Superior': res['ci_upper'],
                'Observações': res['n_obs'],
                'Perfil': classificar_elasticidade(res['elasticidade']),
                'Sig. Estatística': '✅ Significativo' if res['p_value'] < 0.05 else '⚠️ Não Significativo'
            })
        else:
            resultados_elast.append({
                'SKU': sku, 'Categoria': cat,
                'Elasticidade': None, 'R²': None,
                'IC 95% Inferior': None, 'IC 95% Superior': None,
                'Observações': 0, 'Perfil': '—', 'Sig. Estatística': '—'
            })

    df_elast_tab = pd.DataFrame(resultados_elast)

    # Gráfico de barras de elasticidades
    df_elast_validos = df_elast_tab.dropna(subset=['Elasticidade']).sort_values('Elasticidade')
    cores = ['#ef553b' if e <= -1 else '#00cc96' for e in df_elast_validos['Elasticidade']]

    fig_elast_bar = go.Figure(go.Bar(
        x=df_elast_validos['Elasticidade'],
        y=df_elast_validos['SKU'],
        orientation='h',
        marker_color=cores,
        text=df_elast_validos['Elasticidade'].apply(lambda x: f"{x:.2f}"),
        textposition='outside',
        error_x=dict(
            type='data',
            symmetric=False,
            array=(df_elast_validos['IC 95% Superior'] - df_elast_validos['Elasticidade']).tolist(),
            arrayminus=(df_elast_validos['Elasticidade'] - df_elast_validos['IC 95% Inferior']).tolist(),
            color='rgba(255,255,255,0.4)'
        )
    ))
    fig_elast_bar.add_vline(x=-1, line_dash="dash", line_color="#ffd700",
                             annotation_text="Limiar Elástico/Inelástico (−1)", annotation_position="top right")
    fig_elast_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        height=420, margin=dict(l=0, r=60, t=20, b=0),
        xaxis_title="Elasticidade-Preço da Demanda (EPD)"
    )
    st.plotly_chart(fig_elast_bar, use_container_width=True)
    st.caption("🟢 Verde = Inelástico (EPD > −1) — repasses de preço preservam receita | 🔴 Vermelho = Elástico (EPD ≤ −1) — repasses destróem volume | Barras de erro = Intervalo de Confiança 95%")

    # Tabela formatada
    df_elast_exibe = df_elast_tab.copy()
    df_elast_exibe['Elasticidade'] = df_elast_exibe['Elasticidade'].apply(lambda x: f"{x:.3f}" if x is not None else "—")
    df_elast_exibe['R²'] = df_elast_exibe['R²'].apply(lambda x: f"{x:.3f}" if x is not None else "—")
    df_elast_exibe['IC 95% Inferior'] = df_elast_exibe['IC 95% Inferior'].apply(lambda x: f"{x:.3f}" if x is not None else "—")
    df_elast_exibe['IC 95% Superior'] = df_elast_exibe['IC 95% Superior'].apply(lambda x: f"{x:.3f}" if x is not None else "—")
    st.dataframe(df_elast_exibe, use_container_width=True, height=280)

    # Exportação
    st.download_button(
        label="📥 Exportar Painel de Elasticidades (Excel)",
        data=exportar_excel(df_elast_tab),
        file_name="priceops_elasticidades.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- ANÁLISE INDIVIDUAL ---
    st.markdown("---")
    st.subheader("🔬 Análise Individual de Produto")

    produto_selecionado = st.selectbox("Selecione o Ativo para Modelagem Detalhada:", skus)
    df_prod = df_hist_global[df_hist_global['SKU'] == produto_selecionado].copy()
    res_individual = calcular_elasticidade_produto(df_hist_global, produto_selecionado)

    if res_individual and len(df_prod) > 2:
        elasticidade_calculada = res_individual['elasticidade']
        r2 = res_individual['r2']
        p_value = res_individual['p_value']

        # Métricas do modelo
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        col_e1.metric("Elasticidade (EPD)", f"{elasticidade_calculada:.3f}")
        col_e2.metric("Coef. de Determinação (R²)", f"{r2:.3f}",
                      help="Indica o quanto a variação de preço explica a variação de volume. R² > 0.7 é considerado forte.")
        col_e3.metric("Perfil da Demanda", classificar_elasticidade(elasticidade_calculada))
        col_e4.metric("Sig. Estatística (p-valor)", f"{p_value:.4f}",
                      delta="Confiável" if p_value < 0.05 else "Atenção: p > 0.05",
                      delta_color="normal" if p_value < 0.05 else "inverse")

        # Qualidade do modelo
        if r2 < 0.4:
            st.warning(f"⚠️ R² = {r2:.3f} — Ajuste baixo. A variação de preço explica pouco do comportamento da demanda. Outros fatores (sazonalidade, promoções, concorrência) podem estar dominando. Use este resultado com cautela.")
        elif r2 < 0.7:
            st.info(f"ℹ️ R² = {r2:.3f} — Ajuste moderado. O modelo captura parte relevante do comportamento, mas há fatores não observados.")
        else:
            st.success(f"✅ R² = {r2:.3f} — Bom ajuste. O modelo explica com consistência a relação preço-volume deste SKU.")

        # Curva de demanda
        col_g1, col_g2 = st.columns([3, 2])
        with col_g1:
            st.write("**Curva de Demanda Ajustada (Preço × Volume)**")
            fig = px.scatter(
                df_prod, x="Preco_Praticado", y="Volume_Vendido",
                trendline="ols", trendline_color_override="#ef553b",
                labels={"Preco_Praticado": "Preço Faturado (R$)", "Volume_Vendido": "Demanda (Unidades)"}
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=0, r=0, t=10, b=0))
            fig.update_traces(marker=dict(size=10, color="#636efa", opacity=0.7))
            st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.write("**Evolução Temporal**")
            df_prod_sorted = df_prod.sort_values('Data')
            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(x=df_prod_sorted['Data'], y=df_prod_sorted['Preco_Praticado'],
                                         name='Preço', line=dict(color='#636efa'), yaxis='y'))
            fig_ts.add_trace(go.Scatter(x=df_prod_sorted['Data'], y=df_prod_sorted['Volume_Vendido'],
                                         name='Volume', line=dict(color='#00cc96', dash='dot'), yaxis='y2'))
            fig_ts.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(title='Preço (R$)', showgrid=False),
                yaxis2=dict(title='Volume (Unid)', overlaying='y', side='right'),
                legend=dict(orientation='h', y=1.1)
            )
            st.plotly_chart(fig_ts, use_container_width=True)

        # Simulador What-If
        st.markdown("---")
        st.subheader("🔮 Simulador de Cenários What-If")

        # Usa preço atual da Base_Atual (não média histórica)
        preco_base_atual = float(df_base_global.loc[df_base_global['SKU'] == produto_selecionado, 'Preco_Atual_R$'].values[0])
        vol_base_atual = float(df_base_global.loc[df_base_global['SKU'] == produto_selecionado, 'Volume_Mensal_Unid'].values[0])

        col_sim1, col_sim2 = st.columns([1, 2])
        with col_sim1:
            variacao_preco_pct = st.number_input(
                "Estratégia de Repasse (%)",
                min_value=-50.0, max_value=50.0, value=5.0, step=0.5, format="%.1f"
            )
            st.caption(f"Referência: Preço atual = {formata_br(preco_base_atual)} | Volume atual = {formata_br(vol_base_atual, is_moeda=False, is_int=True)} unid.")

        variacao_vol_pct = (variacao_preco_pct / 100) * elasticidade_calculada
        novo_preco = preco_base_atual * (1 + (variacao_preco_pct / 100))
        novo_volume = vol_base_atual * (1 + variacao_vol_pct)
        faturamento_antigo = preco_base_atual * vol_base_atual
        faturamento_novo = novo_preco * novo_volume
        variacao_faturamento = faturamento_novo - faturamento_antigo
        variacao_faturamento_pct = (variacao_faturamento / faturamento_antigo) * 100

        with col_sim2:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Novo Preço", formata_br(novo_preco), f"{variacao_preco_pct:+.1f}%")
            c2.metric("Projeção Demanda", formata_br(novo_volume, is_moeda=False, is_int=True), f"{variacao_vol_pct*100:+.1f}%")
            c3.metric("Faturamento Projetado", formata_br(faturamento_novo),
                      delta=f"{variacao_faturamento_pct:+.1f}%",
                      delta_color="normal" if variacao_faturamento >= 0 else "inverse")
            c4.metric("Δ Faturamento Absoluto", formata_br(abs(variacao_faturamento)),
                      delta="Ganho" if variacao_faturamento >= 0 else "Perda",
                      delta_color="normal" if variacao_faturamento >= 0 else "inverse")

    else:
        st.warning(f"O produto '{produto_selecionado}' não possui histórico suficiente para modelagem.")


# =================================================================================
# MÓDULO 4: HUB DE CONHECIMENTO
# =================================================================================
elif menu == "4. Hub de Conhecimento":
    st.title("📚 Glossário de Revenue Management & Econometria")
    st.markdown("Base de conhecimento técnico para alinhamento entre as áreas Comercial, Financeira e Pricing.")

    with st.expander("1. Diferença Matemática: Margem Bruta vs. Markup"):
        st.write("""
        O erro mais comum no varejo/distribuição é precificar via **Markup** achando que se trata de **Margem**.
        
        * **Markup:** É o percentual adicionado *sobre o custo*. (Ex: Custo R$ 10 + 30% = R$ 13).
        * **Margem Bruta:** É a retenção *sobre o preço de venda*. (Ex: Lucro R$ 3 / Preço R$ 13 = Margem real de 23%).
        
        *Atenção:* A Margem Bruta nunca chega a 100% (pois sempre há custo), enquanto o Markup não tem limite.
        """)

    with st.expander("2. Margem Bruta vs. Margem de Contribuição"):
        st.write("""
        * **Margem Bruta:** Deduz todos os custos diretos do produto — aquisição, impostos e custos logísticos/operacionais fixos alocados.
        * **Margem de Contribuição (MC):** Deduz apenas os **custos variáveis** (aquisição e impostos). Exclui custos fixos.
        
        A MC é usada para decisões de curto prazo (promoções, negociações pontuais). 
        Precificar apenas pela MC, ignorando custos fixos, pode gerar lucro contábil ilusório no longo prazo.
        """)

    with st.expander("3. Formação de Preço por Dentro (Mark-up Divisor)"):
        st.write("Para garantir uma Margem exata (Target Margin) pagando todos os impostos incidentes, utilizamos o Mark-up Divisor.")
        st.latex(r"Preco = \frac{Custos\ Operacionais}{1 - (\%Impostos + \%Margem\ Desejada)}")
        st.write("*Exemplo:* Custo R$ 10, Impostos 15%, Margem 20%. Resultado: 10 / (1 − 0,35) = **R$ 15,38**.")

    with st.expander("4. Elasticidade-Preço da Demanda (EPD)"):
        st.write("""
        Mede a sensibilidade do consumidor a variações de preço.
        
        * **Elástica (EPD < −1):** Pequenos aumentos destroem volume significativo. Típico de produtos com substitutos.
        * **Inelástica (EPD entre −1 e 0):** Aumentos geram baixa perda de volume. Típico de essenciais.
        
        O Motor (Módulo 3) usa **Regressão Log-Log (OLS)** sobre o histórico para isolar o coeficiente angular, que representa a elasticidade.
        """)

    with st.expander("5. R² e Confiabilidade do Modelo de Elasticidade"):
        st.write("""
        O **Coeficiente de Determinação (R²)** indica quanto da variação de volume é explicada pela variação de preço:
        
        * **R² > 0.7:** Bom ajuste — o modelo é confiável para simulações.
        * **R² entre 0.4 e 0.7:** Ajuste moderado — use com cautela.
        * **R² < 0.4:** Ajuste fraco — outros fatores dominam (sazonalidade, promoções, concorrência).
        
        O **p-valor** mede a significância estatística: p < 0.05 indica que a relação preço-volume não é aleatória.
        """)

    with st.expander("6. Curva ABC (Princípio de Pareto)"):
        st.write("""
        Classifica o portfólio pela contribuição acumulada ao faturamento:
        
        * **Classe A:** ~20% dos SKUs responsáveis por ~80% do faturamento. Prioridade máxima em pricing e estoque.
        * **Classe B:** ~30% dos SKUs com ~15% do faturamento. Monitoramento regular.
        * **Classe C:** ~50% dos SKUs com ~5% do faturamento. Avaliar custo-benefício de manutenção no portfólio.
        """)

    with st.expander("7. Break-Even Promocional"):
        st.write("Calcula o volume adicional necessário para que um desconto não destrua a massa de margem.")
        st.latex(r"Incremento\ Necesario\ (\%) = \frac{\%\ Desconto}{\%\ Margem\ Atual - \%\ Desconto}")
        st.write("*Exemplo:* Margem 20%, desconto 5% → equipe precisa vender **33% a mais** só para empatar.")

    with st.expander("8. Elasticidade Cruzada e Efeito Halo"):
        st.write("""
        * **Elasticidade Cruzada:** Como o preço do Produto A afeta o volume do Produto B (substitutos ou complementares).
        * **Efeito Halo:** Produto "chamariz" (ex: cerveja barata) arrasta venda de itens rentáveis no mesmo carrinho.
        """)

    with st.expander("9. Price Waterfall (Cascata de Preços)"):
        st.write("""
        Representação visual das perdas entre o Preço de Tabela e o Lucro Retido.
        Identifica onde o dinheiro vaza: descontos, fretes não cobrados, impostos mal calculados, verbas trade.
        Fundamental para diagnóstico de rentabilidade real vs. rentabilidade percebida.
        """)