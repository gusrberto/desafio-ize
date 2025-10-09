import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def get_db_engine():
    """
    Cria e retorna uma engine de conexão do SQLAlchemy
    utilizando DATABASE_URL do arquivo .env
    """

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")
    
    print("Criando engine de conexão com o banco de dados...")
    return create_engine(database_url)

def load_data(df_pacotes: pd.DataFrame, df_eventos: pd.DataFrame):
    """
    Carrega os DataFrames de pacotes e eventos no banco de dados por meio de uma transação.
    - Estratégia "upsert" para ambas as tabela `pacotes` e `eventos_rastreamento`.
    """

    engine = get_db_engine()

    # Context manager para garantir que a conexão seja fechada
    with engine.connect() as conn:
        # Operação de transação, caso ocorra erro acontece o rollback
        with conn.begin() as transaction:
            try:
                # [Pacotes]
                print(f"Iniciando carregamento de {len(df_pacotes)} registros na tabela 'pacotes'...")

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
                print(f"[*] {result_pacotes.rowcount} novos registros de pacotes inseridos.")

                # [Eventos]
                print (f"Iniciando carregamento de {len(df_eventos)} registros na tabela 'eventos_rastreamento'...")

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
                print(f"[*] {result_eventos.rowcount} novos registros de eventos inseridos.")

                print("\nTransação concluída com sucesso.")
            
            except Exception as e:
                print(f"ERRO: Erro na transação. Fazendo rollback...")
                transaction.rollback()
                print(f"Erro: {e}")
                raise
