import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# ===========================
# CONFIGURAÇÕES INICIAIS
# ===========================
st.set_page_config(page_title="📡 Dashboard de Monitoramento", layout="wide")

# ===========================
# CSS GLOBAL (responsividade)
# ===========================
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        padding: 1rem 2rem 2rem 2rem;
    }
    [data-testid="stVerticalBlock"] {
        overflow-x: hidden !important;
    }
    .block-container {
        max-width: 100% !important;
        padding-top: 1rem;
    }
    .rodape {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 40px;
        background-color: #0b0c10;
        border-top: 1px solid #1f2833;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        color: #c5c6c7;
        font-size: 13px;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# ===========================
# CONEXÃO COM GOOGLE SHEETS
# ===========================
SHEET_URL = "https://docs.google.com/spreadsheets/d/18TKqjh2HkbhSsEC8cmj1Ok_NPaRSRYgO/export?format=csv"

@st.cache_data
def carregar_dados():
    df = pd.read_csv(SHEET_URL)
    colunas_esperadas = ["Status", "Cliente", "Sub Cliente", "ID", "Ult Dado", "Numero de telefone cliente", "Observação"]
    for c in colunas_esperadas:
        if c not in df.columns:
            df[c] = ""
    return df

# ===========================
# BOTÃO DE ATUALIZAÇÃO
# ===========================
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Atualizar dados agora"):
        st.cache_data.clear()
        st.rerun()
with col2:
    st.caption("Clique para recarregar os dados mais recentes da planilha.")

# ===========================
# CARREGAR PLANILHA
# ===========================
try:
    df = carregar_dados()
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar a planilha: {e}")
    st.stop()

# ===========================
# SIDEBAR - LOGO + MENU
# ===========================
st.sidebar.image(
    "/home/paulosilva/Downloads/Logo.jpg",
    use_container_width=True,
)
st.sidebar.markdown("### Engecomp Tecnologia")
st.sidebar.markdown("_Monitoramento Remotas Berçário_")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "📂 Escolha uma página:",
    ["Visão Geral", "Subclientes"]
)

# ===========================
# CABEÇALHO PRINCIPAL COM LOGO
# ===========================
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.image("/home/paulosilva/Downloads/Logo.jpg", width=100)
with col_titulo:
    st.markdown(
        "<h1 style='color:#66fcf1; margin-bottom:0;'>📡 Dashboard de Monitoramento</h1>"
        "<h4 style='color:#c5c6c7;'>Engecomp Tecnologia</h4>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ===========================
# PÁGINA 1 - VISÃO GERAL
# ===========================
if pagina == "Visão Geral":
    st.header("📊 Status das Remotas por Cliente")

    total = len(df)
    online = len(df[df["Status"].str.lower() == "online"])
    offline = len(df[df["Status"].str.lower() == "offline"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Remotas", total)
    with col2:
        st.metric("Online", online)
    with col3:
        st.metric("Offline", offline)

    st.markdown("---")

    status_por_cliente = df.groupby(["Cliente", "Status"]).size().reset_index(name="Quantidade")

    fig = px.bar(
        status_por_cliente,
        x="Cliente",
        y="Quantidade",
        color="Cliente",
        hover_data=["Status", "Quantidade"],
        barmode="stack",
        text="Quantidade",
        height=600
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#0b0c10",
        paper_bgcolor="#0b0c10",
        font_color="#ffffff",
        title_font_color="#66fcf1",
        xaxis_tickangle=-45
    )

    # Use config para opções de plotly (sem o argumento deprecado)
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# ===========================
# PÁGINA 2 - SUBCLIENTES
# ===========================
elif pagina == "Subclientes":
    st.header("🔍 Análise por Subcliente")

    cliente_selecionado = st.selectbox(
        "Selecione um Cliente:",
        sorted(df["Cliente"].dropna().unique())
    )

    df_sub = df[df["Cliente"] == cliente_selecionado]

    sub_por_status = df_sub.groupby(["Sub Cliente", "Status"]).size().reset_index(name="Quantidade")

    fig_sub = px.bar(
        sub_por_status,
        x="Sub Cliente",
        y="Quantidade",
        color="Sub Cliente",
        hover_data=["Status", "Quantidade"],
        barmode="stack",
        text="Quantidade",
        height=600
    )
    fig_sub.update_traces(textposition="outside")
    fig_sub.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#0b0c10",
        paper_bgcolor="#0b0c10",
        font_color="#ffffff",
        title_font_color="#66fcf1",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_sub, use_container_width=True, config={"responsive": True})

    st.subheader(f"📋 Tabela de Remotas de {cliente_selecionado}")
    st.dataframe(df_sub, use_container_width=True, height=400)

# ===========================
# DATA DE ATUALIZAÇÃO LOCAL
# ===========================
ultima_atualizacao_local = datetime.now().strftime("%d/%m/%Y %H:%M")

# ===========================
# RODAPÉ FIXO
# ===========================
st.markdown(f"""
    <div class="rodape">
        <div>💻 Desenvolvido por <b style="color:#66fcf1;">Paulo Henrique</b> | Proj.01</div>
        <div>🕒 Última atualização: <b style="color:#66fcf1;">{ultima_atualizacao_local}</b></div>
    </div>
""", unsafe_allow_html=True)

