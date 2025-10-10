import logging
import os
import pandas as pd
from dotenv import load_dotenv
import io

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Retorna uma conexão de banco de dados (padrão DBAPI), detectando
    automaticamente se está rodando em um ambiente Airflow ou local.
    """
    if os.getenv("AIRFLOW_HOME"):
        logger.info("Ambiente Airflow detectado. Usando Airflow Connection 'postgres_app_db'.")
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        hook = PostgresHook(postgres_conn_id="postgres_pipeline_db")
        return hook.get_conn()
    else:
        logger.info("Ambiente local detectado. Carregando .env...")
        load_dotenv()
        database_url = os.getenv("LOCAL_DATABASE_URL")
        if not database_url:
            raise ValueError("LOCAL_DATABASE_URL não definida no .env.")
        import psycopg2
        return psycopg2.connect(database_url)

def load_data(df_pacotes: pd.DataFrame, df_eventos: pd.DataFrame):
    """
    Carrega os DataFrames de pacotes e eventos no banco de dados por meio de uma transação.
    - Estratégia "upsert" para ambas as tabela `pacotes` e `eventos_rastreamento`.
    """
    conn = None

    try:    
        conn = get_db_connection()
        cursor = conn.cursor()

        # [Pacotes]
        logger.info(f"Iniciando carregamento de {len(df_pacotes)} registros na tabela 'pacotes'...")

        # Upsert: Inserir em uma tabela temporária e depois usar 'ON CONFLICT' para
        # inserir apenas pacotes novos no banco
        cursor.execute("""
            CREATE TEMPORARY TABLE pacotes_temp (
                id_pacote INT,
                origem VARCHAR,
                destino VARCHAR         
            ) ON COMMIT DROP;
        """)

        # Converte o DataFrame de pacotes para um CSV em memória
        string_io = io.StringIO()
        df_pacotes.to_csv(string_io, index=False, header=False)
        string_io.seek(0)

        cursor.copy_from(string_io, "pacotes_temp", columns=df_pacotes.columns, sep=',')

        upsert_pacotes_sql = """
            INSERT INTO pacotes (id_pacote, origem, destino)
            SELECT id_pacote, origem, destino
                        FROM pacotes_temp
                        ON CONFLICT (id_pacote) DO NOTHING;
        """
        cursor.execute(upsert_pacotes_sql)
        logger.info(f"[*] {cursor.rowcount} novos registros de pacotes inseridos.")

        # [Eventos]
        logger.info(f"Iniciando carregamento de {len(df_eventos)} registros na tabela 'eventos_rastreamento'...")

        # Upsert: Inserir em uma tabela temporária e depois usar 'ON CONFLICT' para
        # inserir apenas eventos novos no banco
        cursor.execute("""
            CREATE TEMPORARY TABLE eventos_temp (
                id_pacote INT,
                status_rastreamento VARCHAR,
                data_evento TIMESTAMP WITH TIME ZONE         
            ) ON COMMIT DROP;
        """)

        # Converte o DataFrame de eventos para um CSV em memória
        string_io = io.StringIO()
        df_eventos.to_csv(string_io, index=False, header=False)
        string_io.seek(0)

        cursor.copy_from(string_io, "eventos_temp", columns=df_eventos.columns, sep=',')

        upsert_eventos_sql = """
            INSERT INTO eventos_rastreamento (id_pacote, status_rastreamento, data_evento)
            SELECT id_pacote, status_rastreamento, data_evento
                        FROM eventos_temp
                        ON CONFLICT (id_pacote, data_evento) DO NOTHING;
        """
        cursor.execute(upsert_eventos_sql)
        logger.info(f"[*] {cursor.rowcount} novos registros de eventos inseridos.")

        logger.info("Transação concluída com sucesso. Realizando commit...")
        conn.commit()
    
    except Exception as e:
        logger.exception(f"Erro na transação. Fazendo rollback...")
        logger.exception(f"Erro: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
         if conn:
              logger.info("Conexão com banco de dados fechada.")
              conn.close()
