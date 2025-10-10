import logging
import pandas as pd

logger = logging.getLogger(__name__)

def extract_from_csv(file_path: str) -> pd.DataFrame | None:
    """
    Extrai dados de um arquivo CSV, tratando possíveis erros
    e em caso de sucesso retorna um DataFrame
    """

    try:
        logger.info(f"Iniciando a extração do arquivo: {file_path}")
        df = pd.read_csv(file_path)

        if df.empty:
            logger.warning(f"O arquivo '{file_path}' está vazio.")
            return None
        
        logger.info(f"Extração concluída com sucesso. {len(df)} linhas encontradas.")
        return df
    
    except FileNotFoundError:
        logger.error(f"O arquivo não foi encontrado no caminho: {file_path}")
        return None
    except Exception as e:
        logger.exception(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return None
    