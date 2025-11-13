import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from datetime import datetime
import base64
from PIL import Image

# Usuários e senhas (você pode editar aqui)
USERS = {
    "suporte": "engecomp",
    "Suporte_adm": "1111",
    "suporte_01": "0000"
}

# ======== CONVERTER IMAGEM LOCAL PARA BASE64 ========
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Caminho da imagem local
logo_path = os.path.join(os.path.dirname(__file__), "Logo_completo.jpg")
if os.path.exists(logo_path):
    logo_base64 = get_base64(logo_path)
else:
    logo_base64 = ""

# ==================================
# SISTEMA DE LOGIN SIMPLES COM FUNDO
# ==================================
# Caminho da imagem de fundo
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "logo_login.jpg")

# CSS para o fundo
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url('file://{BACKGROUND_PATH}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
""", unsafe_allow_html=True)
# Controle de sessão
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔐 Acesso Restrito")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USERS and USERS[usuario] == senha:
            st.session_state["autenticado"] = True
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()



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
    colunas_esperadas = ["Status", "Cliente", "Sub Cliente", "ID", "Ult Dado", "Observação"]
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
st.sidebar.image(os.path.join(os.path.dirname(__file__), "Logo.jpg"), width=150)
st.sidebar.markdown("### Engecomp Tecnologia")
st.sidebar.markdown("_Monitoramento Remotas Berçário_")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "📂 Escolha uma página:",
    ["Visão Geral", "Subclientes", "Comparar"]
)

# ===========================
# CABEÇALHO PRINCIPAL COM LOGO
# ===========================
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.image(os.path.join(os.path.dirname(__file__), "Logo.jpg"), width=100)
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
# 📄 COMPARAR E ATUALIZAR PLANILHAS (COM HISTÓRICO + LAYOUT MELHORADO)
# ===========================

elif pagina == "Comparar":
    st.header("📊 Atualizar Base com Novas Remotas")

    st.markdown("""
    Faça upload da **nova planilha (.xlsx)**.  
    O sistema vai:
    - Comparar com `novembro bercario.xlsx` (planilha base);
    - Adicionar automaticamente as **Remotas que Entraram 😁**;
    - Identificar as **Remotas que Saíram 😢**;
    - Gerar planilhas atualizadas e o histórico mensal.
    """)

    novo_arquivo = st.file_uploader("📤 Envie a nova planilha (.xlsx)", type=["xlsx"])

    if novo_arquivo is not None:
        try:
            # Carrega base e nova planilha
            df_base = pd.read_excel("novembro bercario.xlsx")
            df_novo = pd.read_excel(novo_arquivo)
            st.success("✅ Nova planilha carregada com sucesso!")

            # Define colunas padrão (estrutura da base)
            colunas_esperadas = ["Status", "Cliente", "Sub Cliente", "ID", "Ult Dado", "Observação"]
            for c in colunas_esperadas:
                if c not in df_base.columns:
                    df_base[c] = ""
                if c not in df_novo.columns:
                    df_novo[c] = ""

            # Reordena colunas e normaliza IDs
            df_base = df_base[colunas_esperadas]
            df_novo = df_novo[colunas_esperadas]

            df_base["ID"] = df_base["ID"].astype(str).str.strip().str.replace(".0", "", regex=False)
            df_novo["ID"] = df_novo["ID"].astype(str).str.strip().str.replace(".0", "", regex=False)

            # Remove duplicados
            df_base = df_base.drop_duplicates(subset="ID")
            df_novo = df_novo.drop_duplicates(subset="ID")

            # Filtra novos e removidos (remotas)
            ids_base = set(df_base["ID"])
            ids_novo = set(df_novo["ID"])

            df_remotas_entraram = df_novo[~df_novo["ID"].isin(ids_base)].copy()
            df_remotas_sairam = df_base[~df_base["ID"].isin(ids_novo)].copy()

            # Garante colunas no padrão
            for df_temp in [df_remotas_entraram, df_remotas_sairam]:
                for c in colunas_esperadas:
                    if c not in df_temp.columns:
                        df_temp[c] = ""
                df_temp = df_temp[colunas_esperadas]

            # Atualiza base
            df_atualizada = pd.concat([df_base, df_remotas_entraram], ignore_index=True)
            df_atualizada = df_atualizada[colunas_esperadas]

            # Salva resultados
            df_atualizada.to_excel("Atualizada.xlsx", index=False)
            df_remotas_entraram.to_excel("Remotas_Entraram.xlsx", index=False)
            df_remotas_sairam.to_excel("Remotas_Sairam.xlsx", index=False)

            count_entraram = len(df_remotas_entraram)
            count_sairam = len(df_remotas_sairam)

            # ==============================
            # 📊 Exibe resultados lado a lado
            # ==============================
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🟢 Remotas que Entraram 😁")
                if count_entraram > 0:
                    st.success(f"{count_entraram} remotas novas adicionadas")
                    st.dataframe(df_remotas_entraram, use_container_width=True, height=300)
                    st.download_button(
                        "⬇️ Baixar Remotas_Entraram.xlsx",
                        data=open("Remotas_Entraram.xlsx", "rb"),
                        file_name="Remotas_Entraram.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("Nenhuma remota nova encontrada.")

            with col2:
                st.markdown("### 🔴 Remotas que Saíram 🚀")
                if count_sairam > 0:
                    st.error(f"{count_sairam} remotas foram removidas")
                    st.dataframe(df_remotas_sairam, use_container_width=True, height=300)
                    st.download_button(
                        "⬇️ Baixar Remotas_Sairam.xlsx",
                        data=open("Remotas_Sairam.xlsx", "rb"),
                        file_name="Remotas_Sairam.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("Nenhuma remota removida encontrada.")

            st.download_button(
                "⬇️ Baixar Atualizada.xlsx",
                data=open("Atualizada.xlsx", "rb"),
                file_name="Atualizada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.info(f"📘 Planilha final contém **{len(df_atualizada)} registros**.")

            # ==============================
            # 🧾 Registro histórico
            # ==============================
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            historico_path = "historico_comparacoes.xlsx"

            if os.path.exists(historico_path):
                historico = pd.read_excel(historico_path)
            else:
                historico = pd.DataFrame(columns=["Data", "Remotas que Entraram 😁", "Remotas que Saíram 🚀"])

            novo_registro = pd.DataFrame({
                "Data": [data_hoje],
                "Remotas que Entraram 😁": [count_entraram],
                "Remotas que Saíram 🚀": [count_sairam]
            })

            historico = pd.concat([historico, novo_registro], ignore_index=True)
            historico.to_excel(historico_path, index=False)

            # ==============================
            # 📈 Gráfico de linha (histórico ajustável)
            # ==============================
            max_valor = max(historico[["Remotas que Entraram 😁", "Remotas que Saíram 🚀"]].max().max(), 20)

            fig = px.line(
                historico,
                x="Data",
                y=["Remotas que Entraram 😁", "Remotas que Saíram 🚀"],
                markers=True,
                title="📊 Evolução de Remotas — Entradas e Saídas ao Longo do Tempo",
            )
            fig.update_layout(
                yaxis=dict(title="Quantidade de Remotas", range=[0, max_valor + 5]),
                xaxis_title="Data",
                legend_title="Categoria",
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")

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

