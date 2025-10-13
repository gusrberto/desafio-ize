import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from src.data import buscar_dados_do_banco
from src.utils import formatar_timedelta

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Logística (Real-Time)",
    page_icon="⚡",
    layout="wide"
)

# Atualização Automática
# Atualiza a página a cada 5 segundos
st_autorefresh(interval=5000, key="datarefresh")

# Construção da Interface do Dashboard
st.title("⚡ Dashboard de Monitoramento de Entregas (Real-Time)")

# 1. Busca os dados a cada atualização da página
df_status, tempo_medio = buscar_dados_do_banco()

# 2. Renderiza a interface
if df_status is not None:
    total_pacotes = int(df_status["total_pacotes"].sum())

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Pacotes por Status Atual")
            fig = px.pie(
                df_status,
                names='status_rastreamento',
                values='total_pacotes',
                title='Distribuição de Status'
            )
            st.plotly_chart(fig, config={"responsive": True})

    with col2:
        with st.container(border=True):
            st.subheader("Tempo Médio de Entrega")
            st.metric(
                label="Média do Envio à Entrega", 
                value=formatar_timedelta(tempo_medio)
            )
        with st.container(border=True):
            st.subheader("Total de Pacotes")
            st.metric(
                label="Total de Pacotes Únicos no Sistema",
                value=total_pacotes
            )

    with st.container(border=True):
        st.subheader("Dados de Status")
        st.dataframe(df_status, width='stretch')
else:
    st.warning("Aguardando dados... Verifique se o consumidor Kafka e o banco de dados estão em execução.")
