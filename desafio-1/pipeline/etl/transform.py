import logging
import pandas as pd
from typing import Tuple

logger = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Realiza a transformação dos dados, retornando dois DataFrames que irão para as
    tabelas `pacotes` e `eventos_rastreamento`
    """

    logger.info("Iniciando a etapa de transformação dos dados...")

    numero_eventos = len(df)
    logger.debug(f"DataFrame recebido com {numero_eventos} registrados.")

    # Cria o DataFrame dos eventos de rastreamento
    df_eventos = df[["id_pacote", "status_rastreamento", "data_atualizacao"]].copy()
    df_eventos.rename(columns={"data_atualizacao": "data_evento"}, inplace=True)
    logger.debug(f"DataFrame de eventos criado com {len(df_eventos)} linhas.")

    # Garante que caso haja produtos duplicados no CSV, somente a primeira encontrada é considerada
    df_pacotes = df[["id_pacote", "origem", "destino"]].copy()
    df_pacotes = df_pacotes.drop_duplicates(subset=["id_pacote"], keep="first")

    logger.info(
        f"Identificados {len(df_pacotes)} únicos a partir de {numero_eventos} eventos."
    )
    logger.info(
        "Transformação concluída. DataFrames para pacotes e eventos estão prontos."
    )

    return df_pacotes, df_eventos
