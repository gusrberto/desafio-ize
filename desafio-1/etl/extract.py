import pandas as pd

def extract_from_csv(file_path: str) -> pd.DataFrame | None:
    """
    Extrai dados de um arquivo CSV, tratando possíveis erros
    e em caso de sucesso retorna um DataFrame
    """

    try:
        print(f"Iniciando a extração do arquivo: {file_path}")
        df = pd.read_csv(file_path)

        if df.empty:
            print(f"AVISO: O arquivo '{file_path}' está vazio.")
            return None
        
        print(f"Extração concluída com sucesso. {len(df)} linhas encontradas.")
        return df
    
    except FileNotFoundError:
        print(f"ERRO: O arquivo não foi encontrado no caminho: {file_path}")
        return None
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return None
    