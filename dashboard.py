import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import json  # Para ler ficheiros .txt com JSON
import requests  # Para importação automática de URL

# ----- CONFIGURAÇÃO DA PÁGINA -----
st.set_page_config(page_title="Escola Profissional da Ilha de São Jorge", layout="wide")

# ----- ESTILO VISUAL -----
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #f9f9f9;
        }
        .main { padding: 20px; }
        h1, h2, h3, h4 {
            color: #1B2A49;
            animation: fadeInDown 1s ease-out;
        }
        @keyframes fadeInDown {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 4px;
        }
        .stButton button {
            background-color: #40A86B;
            color: white;
            font-weight: bold;
            animation: fadeInDown 1.2s ease-out;
        }
        .stDownloadButton button {
            background-color: #1B2A49;
            color: white;
            font-weight: bold;
            animation: fadeInDown 1.4s ease-out;
        }
        div[data-testid="stSidebar"] > div:first-child {
            background-color: #ffffff !important;
            color: #000000 !important;
            animation: fadeInDown 1s ease-out;
        }
        div[data-testid="stSidebar"] * {
            color: #000000 !important;
        }
        .login-title {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ----- COORDENADAS DAS ILHAS -----
ilhas_acores = {
    "São Jorge": {"latitude": 38.6667, "longitude": -28.0833},
    "Pico": {"latitude": 38.4694, "longitude": -28.3994},
    "Faial": {"latitude": 38.5969, "longitude": -28.6247},
    "Terceira": {"latitude": 38.7306, "longitude": -27.2167},
    "S. Miguel": {"latitude": 37.7333, "longitude": -25.6667},
    "Santa Maria": {"latitude": 36.9667, "longitude": -25.1200},
    "Graciosa": {"latitude": 39.0667, "longitude": -28.0100},
    "Flores": {"latitude": 39.4500, "longitude": -31.1333},
    "Corvo": {"latitude": 39.6833, "longitude": -31.1167}
}

# ----- LOGIN -----
def login():
    st.markdown('<div class="login-title">', unsafe_allow_html=True)
    st.image(
        "https://www.episj.com/wp-content/uploads/2024/05/logo_2024_2-green-2.png",
        width=1000
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("Digite suas credenciais para continuar:")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Entrar"):
        if username == "admin" and password == "admin":
            st.session_state['logged_in'] = True
            st.success("Bem-vindo, admin!")
            st.rerun()
        else:
            st.error("Credenciais inválidas")

from sqlalchemy import create_engine

# Função para importar inscrições diretamente da base de dados online
@st.cache_data
def importar_dados_sql():
    try:
        db_user = "episjacores_dash"
        db_pass = "4$B7yne*(cN("
        db_host = "mysql.episj.com"
        db_port = "3306"
        db_name = "episjacores_new24"
        table_name = "inscricoes"

        engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        st.success("✅ Dados importados com sucesso da base de dados online!")
        return df
    except Exception as e:
        st.error(f"❌ Erro ao importar dados da base de dados: {e}")
        return None

# ----- EXECUÇÃO PRINCIPAL -----
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login()
else:
    st.markdown("# Escola Profissional da Ilha de São Jorge")
    st.markdown("### Dashboard de Pré-Inscrições")

    # Importação manual + botão de importação automática ao lado do uploader
    col_uploader, col_auto = st.columns([1, 1])
    df = None
    with col_uploader:
        uploaded_file = st.file_uploader(
            "📁 Carrega o ficheiro CSV, Excel ou TXT com os dados",
            type=["csv", "xlsx", "txt"], key="uploader"
        )
    with col_auto:
        if st.button("🔄 Importar JSON do site", key="auto_import"):
            try:
                url = "http://www.episj.com/sub/test.txt"
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200 and resp.text.strip():
                    data = json.loads(resp.text)
                    if isinstance(data, dict): data = [data]
                    df = pd.DataFrame(data)
                    st.success("Importação automática concluída!")
                else:
                    st.error(f"Falha ao importar: status {resp.status_code}")
            except Exception as e:
                st.error(f"Erro na importação automática: {e}")

        if st.button("🗃️ Importar inscrições da base de dados SQL", key="sql_import"):
            df = importar_dados_sql()

    # Funções utilitárias
    @st.cache_data
    def carregar_dados(f):
        name = f.name.lower()
        if name.endswith(".csv"): return pd.read_csv(f)
        if name.endswith(".txt"):
            txt = f.read().decode("utf-8")
            js = json.loads(txt)
            if isinstance(js, dict): js = [js]
            return pd.DataFrame(js)
        return pd.read_excel(f)

    @st.cache_data
    def calcular_idade(nasc):
        hoje = pd.Timestamp("today")
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

    def calcular_ano_letivo(d):
        if pd.isnull(d): return "Desconhecido"
        return f"{d.year}/{d.year+1}"

    # Se fez upload, processa o ficheiro
    if uploaded_file:
        df = carregar_dados(uploaded_file)
        st.success("Ficheiro carregado com sucesso!")

    # Continua apenas se df estiver preenchido
    if df is not None:
        df.columns = df.columns.str.strip().str.replace('"','')
        ext = uploaded_file.name.lower().split('.')[-1] if uploaded_file else ''

        # Datas e cálculo de ano letivo
        if "Created" in df.columns and ext in ["csv","xlsx"]:
            df["Created"] = pd.to_datetime(df["Created"], errors='coerce', dayfirst=True)
            df["Ano Letivo"] = df["Created"].apply(calcular_ano_letivo)
        elif "Ano Letivo" not in df.columns:
            df["Ano Letivo"] = "Desconhecido"

        # Data de Nascimento e Idade
        if "Data de Nascimento" in df.columns:
            df["Data de Nascimento"] = pd.to_datetime(df["Data de Nascimento"], errors='coerce', dayfirst=True)
            df["Idade Calculada"] = df["Data de Nascimento"].apply(lambda x: calcular_idade(x) if pd.notnull(x) else None)
        else:
            df["Idade Calculada"] = None

        # Sidebar e filtros
        st.sidebar.image(
            "https://www.episj.com/wp-content/uploads/2024/05/logo_2024_2-green-2.png",
            width=500
        )
        st.sidebar.header("🔎 Filtros")

        anos = sorted(df["Ano Letivo"].dropna().unique(), reverse=True)
        ano_letivo = st.sidebar.selectbox("Ano Letivo", anos)
        df_filtrado = df[df["Ano Letivo"] == ano_letivo]

        curso_selecionado = st.sidebar.selectbox(
            "Curso (Primeira Opção)",
            ["Todos"] + list(df_filtrado.get("Primeira Opção", []))
        )
        if curso_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Primeira Opção"] == curso_selecionado]

        escola_selecionada = st.sidebar.selectbox(
            "Escola de Origem",
            ["Todas"] + list(df_filtrado.get("Escola", []))
        )
        if escola_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Escola"] == escola_selecionada]

        if st.sidebar.button("❌ Limpar Filtros"):
            st.session_state['logged_in'] = False
            st.rerun()

        # Ocultar colunas desnecessárias
        colunas_a_ocultar = [
            "Apelido", "text field", "endereço eletrónico.1",
            "text fiel.1", "text fieldmail", "text fieldidade"
        ]
        df_filtrado = df_filtrado.drop(columns=colunas_a_ocultar, errors='ignore')

        # 🔁 GUARDA O DF FILTRADO PARA A PÁGINA DE INSCRIÇÕES
        st.session_state["df_filtrado"] = df_filtrado

        # Vista Geral dos Dados
        with st.expander(f"👁️ Vista Geral dos Dados ({ano_letivo})", expanded=True):
            st.dataframe(df_filtrado, use_container_width=True)

        # Gráficos iniciais
        col1, col2 = st.columns(2)
        with col1:
            fig_ilha = px.histogram(
                df_filtrado, x="Ilha", title="Distribuição por Ilha",
                color_discrete_sequence=["#3b82f6"]
            )
            st.plotly_chart(fig_ilha, use_container_width=True)
        with col2:
            fig_idade = px.histogram(
                df_filtrado, x="Idade Calculada", nbins=20,
                title="Distribuição Etária", color_discrete_sequence=["#f59e0b"]
            )
            st.plotly_chart(fig_idade, use_container_width=True)

        # Mapa + Tabela lado a lado
        df_map = df_filtrado.copy()
        df_map["Ilha"] = df_map["Ilha"].replace({"Sao Jorge": "São Jorge", "São Miguel": "S. Miguel"})
        df_map["latitude"] = df_map["Ilha"].map(lambda x: ilhas_acores[x]["latitude"])
        df_map["longitude"] = df_map["Ilha"].map(lambda x: ilhas_acores[x]["longitude"])
        inscricoes_por_ilha = df_map.groupby(
            ["Ilha", "latitude", "longitude"]
        ).size().reset_index(name="count")
        inscricoes_por_ilha["label"] = inscricoes_por_ilha.apply(
            lambda row: f"{row['Ilha']}\n{row['count']}", axis=1
        )
        color_map = {
            "Santa Maria": "yellow", "S. Miguel": "green",
            "Terceira": "#C8A2C8", "Graciosa": "white", "São Jorge": "brown",
            "Pico": "grey", "Faial": "blue", "Flores": "pink", "Corvo": "black"
        }
        fig_map = px.scatter_mapbox(
            inscricoes_por_ilha,
            lat="latitude", lon="longitude",
            size="count", size_max=25,
            text="label", hover_name="Ilha",
            color="Ilha", color_discrete_map=color_map,
            zoom=6, center={"lat": 37.7, "lon": -28.0},
            mapbox_style="open-street-map"
        )
        fig_map.update_traces(textposition="top center")

        st.markdown("### 🗺️ Mapa de Inscrições e 📋 Inscrições por Escola")
        col_map, col_table = st.columns(2)
        with col_map:
            st.plotly_chart(fig_map, use_container_width=True)
        with col_table:
            if "Escola" in df_filtrado.columns:
                tabela_escolas = df_filtrado.groupby(
                    "Escola"
                ).size().reset_index(name="Número de Inscrições")
                st.dataframe(tabela_escolas, use_container_width=True)

        # Gráfico de idades 14-25
        df_idade_filtrada = df_filtrado[
            (df_filtrado["Idade Calculada"] >= 14) &
            (df_filtrado["Idade Calculada"] <= 25)
        ]
        st.markdown("### 📊 Gráfico de Idades (14 a 25 anos)")
        fig_idade_filtrada = px.histogram(
            df_idade_filtrada, x="Idade Calculada", nbins=20,
            title="Distribuição Etária (14 a 25 anos)",
            color_discrete_sequence=["#9333ea"]
        )
        st.plotly_chart(fig_idade_filtrada, use_container_width=True)

        # Gráfico de gênero
        if "Género" in df_filtrado.columns:
            st.markdown("### 🧑‍🤝‍🧑 Gráfico de Distribuição por Género")
            fig_genero = px.pie(
                df_filtrado, names="Género",
                title="Distribuição de Inscrições por Género",
                color_discrete_sequence=["#40A86B", "#1B2A49", "#D5D5D5"]
            )
            st.plotly_chart(fig_genero, use_container_width=True)

        # Inscrições por primeira opção
        if "Primeira Opção" in df_filtrado.columns:
            st.markdown("### 📊 Inscrições por Primeira Opção")
            tabela_primeira_opcao = df_filtrado.groupby(
                "Primeira Opção"
            ).size().reset_index(name="Número de Inscrições")
            st.dataframe(tabela_primeira_opcao, use_container_width=True)

        # Cursos escolhidos
        st.markdown("### 🧑‍🎓 Cursos Escolhidos")
        c1, c2, c3 = st.columns(3)
        with c1:
            fig1 = px.histogram(
                df_filtrado, x="Primeira Opção",
                title="🎯 Primeira Opção",
                color_discrete_sequence=["#40A86B"]
            )
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.histogram(
                df_filtrado, x="Segunda Opção",
                title="🥈 Segunda Opção",
                color_discrete_sequence=["#1B2A49"]
            )
            st.plotly_chart(fig2, use_container_width=True)
        with c3:
            fig3 = px.histogram(
                df_filtrado, x="Terceira Opção",
                title="🥉 Terceira Opção",
                color_discrete_sequence=["#D5D5D5"]
            )
            st.plotly_chart(fig3, use_container_width=True)

        # Exportação de dados filtrados e gráficos
        st.markdown("### 📥 Exportar Dados Filtrados")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name="Inscricoes")
            st.download_button(
                label="⬇️ Descarregar Excel",
                data=buffer,
                file_name=f"inscricoes_{ano_letivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("👈 Carrega um ficheiro ou importa automaticamente para começar.")
