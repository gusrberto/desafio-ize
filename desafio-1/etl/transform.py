import pandas as pd
from typing import Tuple

def transform(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """ 
    Realiza a transformação dos dados, retornando dois DataFrames que irão para as
    tabelas `pacotes` e `eventos_rastreamento`    
    """

    # Cria o DataFrame dos eventos de rastreamento
    df_eventos = df[["id_pacote", "status_atualizacao", "data_atualizacao"]].copy()
    df_eventos.rename(columns={"data_atualizacao": "data_evento"}, inplace=True)

    # Ordena o DataFrame pela data de atualização decrescente (Atualização mais recente primeiro)
    df_ordenado = df.sort_values(by="data_atualizacao", ascending=False) 

    # Garante que caso haja produtos duplicados no CSV, somente a atualização mais recente é considerada
    df_pacotes_unicos = df_ordenado.drop_duplicates(subset=["id_pacote"], keep='first')
    df_pacotes = df_pacotes_unicos[["id_pacote", "origem", "destino"]].copy()

    return df_pacotes, df_eventos
