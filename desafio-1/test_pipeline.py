from etl.extract import extract_from_csv
from etl.clean_validate import clean_and_validate
from etl.transform import transform
from etl.load import load_data

def run_pipeline():
    df_raw = extract_from_csv("rastreamento.csv")

    if df_raw is not None:
        df_clean = clean_and_validate(df_raw)

        if not df_clean.empty:
            df_pacotes, df_eventos = transform(df_clean)

            load_data(df_pacotes=df_pacotes, df_eventos=df_eventos)

if __name__ == "__main__":
    run_pipeline()