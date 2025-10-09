import pandas as pd
from typing import Tuple

def transform(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """ 
    Realiza a transformação dos dados, retornando dois DataFrames que irão para as
    tabelas `pacotes` e `eventos_rastreamento`    
    """

    # Cria o DataFrame dos eventos de rastreamento
    df_eventos = df[["id_pacote", "status_rastreamento", "data_atualizacao"]].copy()
    df_eventos.rename(columns={"data_atualizacao": "data_evento"}, inplace=True)

    # Garante que caso haja produtos duplicados no CSV, somente a primeira encontrada é considerada 
    df_pacotes = df[["id_pacote", "origem", "destino"]].copy()
    df_pacotes = df_pacotes.drop_duplicates(subset=["id_pacote"], keep='first')

    return df_pacotes, df_eventos
