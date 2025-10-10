import logging
from etl.extract import extract_from_csv
from etl.clean_validate import clean_and_validate
from etl.transform import transform
from etl.load import load_data


def setup_logging():
    """
    Configuração do sistema de logging do pipeline.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_pipeline():
    logging.info("--- Início da Execução do Pipeline ETL ---")

    df_raw = extract_from_csv("rastreamento.csv")

    if df_raw is not None:
        df_clean = clean_and_validate(df_raw)

        if not df_clean.empty:
            df_pacotes, df_eventos = transform(df_clean)

            load_data(df_pacotes=df_pacotes, df_eventos=df_eventos)

    logging.info("--- Fim da Execução do Pipeline ETL ---")


if __name__ == "__main__":
    setup_logging()
    run_pipeline()
