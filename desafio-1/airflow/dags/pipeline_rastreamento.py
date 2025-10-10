from __future__ import annotations
from datetime import datetime
from airflow.sdk import dag, task

from pipeline.etl import extract, clean_validate, transform, load


@dag(
    dag_id="dag_pipeline_rastreamento",
    description="DAG que orquestra o pipeline do rastreamento de pacotes.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["etl", "rastreamento"],
    default_args={"retries": 3},
)
def etl_rastreamento_pipeline():
    """
    ETL de Rastreamento
    Cada parte do pipeline é representada por uma task
    """

    @task(task_id="extrair_dados")
    def task_extract():
        return extract.extract_from_csv("pipeline/rastreamento.csv")

    @task(task_id="limpar_e_validar_dados")
    def task_clean_validate(df_raw):
        return clean_validate.clean_and_validate(df_raw)

    @task(task_id="transformar_dados")
    def task_transform(df_clean):
        return transform.transform(df_clean)

    @task(task_id="carregar_dados")
    def task_load(transformed_data):
        df_pacotes, df_eventos = transformed_data
        load.load_data(df_pacotes, df_eventos)

    # Fluxo das tasks
    df_bruto = task_extract()
    df_limpo = task_clean_validate(df_bruto)
    dados_transformados = task_transform(df_limpo)
    task_load(dados_transformados)


# Instancia a DAG
etl_rastreamento_pipeline()
