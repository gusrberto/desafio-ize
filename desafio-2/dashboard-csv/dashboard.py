import streamlit as st
import plotly.express as px

from src.data import buscar_dados_no_banco
from src.utils import formatar_timedelta

# Configuração da Página
st.set_page_config(
    page_title="Dashboard de Logística",
    page_icon="🚚",
    layout="wide"
)

# Construção da Interface do Dashboard
st.title("🚚 Dashboard de Monitoramento de Entregas")

# Camada de Dados (Realiza as Queries)
df_status, tempo_medio = buscar_dados_no_banco()

# Camada de Visualização (Exibe os KPIs na Dashboard)
if df_status is not None and tempo_medio is not None:
    total_pacotes = int(df_status["total_pacotes"].sum())

    # Colunas da Dashboard
    col1, col2 = st.columns(2)

    with col1:
        # Pie Chart com Pacotes por Status
        with st.container(border=True):
            st.subheader("Pacotes por Status Atual")
            
            fig = px.pie(
                df_status,
                names='status_rastreamento',
                values='total_pacotes',
                title='Distribuição de Status'
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # KPI 1: Tempo Médio de Entrega
        with st.container(border=True):
            st.subheader("Tempo Médio de Entrega")
            if tempo_medio:
                st.metric(
                    label="Média do Envio à Entrega", 
                    value=formatar_timedelta(tempo_medio)
                )
            else:
                st.metric(label="Média do Envio à Entrega", value="N/A")

        # KPI 2: Total de Pacotes
        with st.container(border=True):
            st.subheader("Total de Pacotes")
            st.metric(
                label="Total de Pacotes Únicos no Sistema",
                value=total_pacotes
            )

    # Mostrar a tabela de dados brutos
    with st.container(border=True):
        st.subheader("Dados de Status")
        st.dataframe(df_status)
else:
    st.warning("Não foi possível carregar os dados. Verifique a conexão com o banco de dados.")
    