import pandas as pd

def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza a limpeza e validação dos dados do DataFrame
    - Remove espaços extras
    - Valida e converte os tipos de dados
    - Remove linhas com dados inválidos ou ausentes
    """
    print("Iniciando limpeza e validação dos dados...")

    # Limpeza nos campos de texto do CSV
    colunas_texto = ["origem", "destino", "status_rastreamento"]
    for col in colunas_texto:
        # Garante que a coluna é do tipo string
        df[col] = df[col].astype(str).str.strip()

    # Validação e conversão de tipos

    # Tenta converter "id_pacote" para numérico, se não conseguir transforma em NaN
    df["id_pacote"] = pd.to_numeric(df["id_pacote"], errors='coerce')
    # Tenta converter "data_atualizacao" de Zulu Time para datetime. Se não conseguir, transforma em NaT
    df["data_atualizacao"] = pd.to_datetime(df["data_atualizacao"], errors='coerce')

    # Tratamento de dados inválidos/ausentes
    linhas_originais = len(df)
    linhas_invalidas = df[df.isnull().any(axis=1)] # Cópia das linhas inválidas para análise

    if not linhas_invalidas.empty:
        print(f"AVISO: Foram encontradas {len(linhas_invalidas)} linhas com dados inválidos/ausentes. Elas serão removidas")
        print("Linhas removidas:")
        print(linhas_invalidas)

    # Remove as linhas que tenham qualquer valor nulo (NaN ou NaT)
    df.dropna(inplace=True)

    # Com os NaN removidos, volta o tipo da coluna para int
    df["id_pacote"] = df["id_pacote"].astype(int)

    print(f"Limpeza concluída. {len(df)}/{linhas_originais} linhas válidas restantes.")

    return df