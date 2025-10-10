import logging
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from airflow.providers.postgres.hooks.postgres import PostgresHook

def get_db_url() -> str:
    """
    Obtém a URL de conexão do banco de dados, detectando
    se está rodando em um ambiente Airflow ou local.
    """

    if os.getenv("AIRFLOW_HOME"):
        logger.info("Ambiente Airflow detectado. Usando Airflow Connection 'postgres_pipeline_db'.")
        hook = PostgresHook(postgres_conn_id="postgres_pipeline_db")
        return hook.get_uri()
    else:
        logger.info("Amiente local detectado. Carregando .env e usando 'LOCAL_DATABASE_URL'.")
        load_dotenv()
        database_url = os.getenv("LOCAL_DATABASE_URL")
        if not database_url:
            raise ValueError("A variável de ambiente LOCAL_DATABASE_URL não foi definida no arquivo .env.")
    
        return database_url

def load_data(df_pacotes: pd.DataFrame, df_eventos: pd.DataFrame):
    """
    Carrega os DataFrames de pacotes e eventos no banco de dados por meio de uma transação.
    - Estratégia "upsert" para ambas as tabela `pacotes` e `eventos_rastreamento`.
    """

    db_url = get_db_url()
    engine = create_engine(db_url)

    # Context manager para garantir que a conexão seja fechada
    with engine.connect() as conn:
        # Operação de transação, caso ocorra erro acontece o rollback
        with conn.begin() as transaction:
            try:
                # [Pacotes]
                logger.info(f"Iniciando carregamento de {len(df_pacotes)} registros na tabela 'pacotes'...")

                # Upsert: Inserir em uma tabela temporária e depois usar 'ON CONFLICT' para
                # inserir apenas pacotes novos no banco
                conn.execute(text("""
                    CREATE TEMPORARY TABLE pacotes_temp (
                        id_pacote INT,
                        origem VARCHAR,
                        destino VARCHAR         
                    ) ON COMMIT DROP;
                """))
                df_pacotes.to_sql("pacotes_temp", conn, if_exists='append', index=False)

                upsert_pacotes_sql = text("""
                    INSERT INTO pacotes (id_pacote, origem, destino)
                    SELECT id_pacote, origem, destino
                                  FROM pacotes_temp
                                  ON CONFLICT (id_pacote) DO NOTHING;
                """)
                result_pacotes = conn.execute(upsert_pacotes_sql)
                logger.info(f"[*] {result_pacotes.rowcount} novos registros de pacotes inseridos.")

                # [Eventos]
                logger.info(f"Iniciando carregamento de {len(df_eventos)} registros na tabela 'eventos_rastreamento'...")

                # Upsert: Inserir em uma tabela temporária e depois usar 'ON CONFLICT' para
                # inserir apenas eventos novos no banco
                conn.execute(text("""
                    CREATE TEMPORARY TABLE eventos_temp (
                        id_pacote INT,
                        status_rastreamento VARCHAR,
                        data_evento TIMESTAMP WITH TIME ZONE         
                    ) ON COMMIT DROP;
                """))
                df_eventos.to_sql('eventos_temp', conn, if_exists='append', index=False)

                upsert_eventos_sql = text("""
                    INSERT INTO eventos_rastreamento (id_pacote, status_rastreamento, data_evento)
                    SELECT id_pacote, status_rastreamento, data_evento
                                  FROM eventos_temp
                                  ON CONFLICT (id_pacote, data_evento) DO NOTHING;
                """)
                result_eventos = conn.execute(upsert_eventos_sql)
                logger.info(f"[*] {result_eventos.rowcount} novos registros de eventos inseridos.")

                logger.info("Transação concluída com sucesso.")
            
            except Exception as e:
                logger.exception(f"Erro na transação. Fazendo rollback...")
                transaction.rollback()
                logger.exception(f"Erro: {e}")
                raise
