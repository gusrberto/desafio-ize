import logging
import os
from dotenv import load_dotenv
import psycopg2

logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Retorna uma conexão de banco de dados (padrão DBAPI) para o TimescaleDB.
    """

    logger.info("Carregando .env...")
    load_dotenv()
    database_url = os.getenv("TIMESCALE_DATABASE_URL")
    if not database_url:
        raise ValueError("TIMESCALE_DATABASE_URL não definida no .env.")

    return psycopg2.connect(database_url)


def load_single_record(pacote_data: dict, evento_data: dict):
    """
    Carrega um único pacote e evento no TimescaleDB de forma idempotente.
    Gerencia sua própria conexão e transação.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Upsert na tabela 'pacotes'
        upsert_pacote_sql = """
            INSERT INTO pacotes (id_pacote, origem, destino)
            VALUES (%(id_pacote)s, %(origem)s, %(destino)s)
            ON CONFLICT (id_pacote) DO NOTHING;
        """
        cursor.execute(upsert_pacote_sql, pacote_data)
        logger.info(f"[*] {cursor.rowcount} novos registros de pacotes inseridos.")

        # 2. Upsert na tabela 'eventos_rastreamento'
        upsert_evento_sql = """
            INSERT INTO eventos_rastreamento (id_pacote, status_rastreamento, data_evento)
            VALUES (%(id_pacote)s, %(status_rastreamento)s, %(data_evento)s)
            ON CONFLICT (id_pacote, data_evento) DO NOTHING;
        """
        cursor.execute(upsert_evento_sql, evento_data)
        logger.info(f"[*] {cursor.rowcount} novos registros de eventos inseridos.")

        # Se tudo deu certo, comita a transação
        conn.commit()
        logger.info(
            f"Registro para o pacote {pacote_data['id_pacote']} processado com sucesso."
        )

    except Exception as e:
        logger.exception(
            "ERRO: Falha ao carregar registro único. Realizando rollback..."
        )
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
