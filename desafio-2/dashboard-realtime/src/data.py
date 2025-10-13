import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def buscar_dados_do_banco():
    """
    Conecta ao TimescaleDB e executa as queries para os KPIs.
    """
    print("Buscando dados no banco...")
    load_dotenv('.env')
    db_url = os.getenv("TIMESCALE_DATABASE_URL")
    if not db_url:
        st.error("A variável TIMESCALE_DATABASE_URL não foi encontrada no arquivo .env.")
        return None, None

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Query #1: Contagem de pacotes por status atual
            query_status = text("""
                WITH ultimo_evento AS (
                    SELECT 
                        id_pacote, 
                        status_rastreamento, 
                        ROW_NUMBER() OVER(PARTITION BY id_pacote ORDER BY data_evento DESC) as rn
                    FROM eventos_rastreamento             
                )
                SELECT
                    status_rastreamento,
                    COUNT(id_pacote) AS total_pacotes
                FROM ultimo_evento
                WHERE rn = 1
                GROUP BY status_rastreamento;
            """)
            df_status = pd.read_sql(query_status, conn)

            # Query #2: Tempo médio de entrega
            query_tempo_entrega = text("""
                WITH entregas_finalizadas AS (
                    SELECT
                        id_pacote,
                        MIN(data_evento) AS data_inicio,
                        MAX(CASE 
                                WHEN status_rastreamento = 'ENTREGUE' THEN data_evento 
                                ELSE NULL 
                            END) AS data_entrega
                    FROM
                        eventos_rastreamento
                    GROUP BY id_pacote                
                )
                                   
                SELECT
                    AVG(data_entrega - data_inicio) AS tempo_medio_entrega
                FROM
                    entregas_finalizadas
                WHERE
                    data_entrega IS NOT NULL;
            """)
            tempo_medio = conn.execute(query_tempo_entrega).scalar_one_or_none()

        return df_status, tempo_medio
    except Exception as e:
        st.error(f"Erro ao conectar ou buscar dados do banco: {e}")
        return None, None