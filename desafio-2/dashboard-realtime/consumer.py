import json
import logging
from kafka import KafkaConsumer

from etl.clean_validate import clean_validate_single_record
from etl.transform import transform_single_record
from etl.load import load_single_record

def setup_logging():
    """
    Configuração do sistema de logging do pipeline.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

logger = logging.getLogger(__name__)

KAFKA_BROKER_URL = "localhost:9094"
TOPIC_NAME = "eventos_rastreamento"
CONSUMER_GROUP_ID = "rastreamento_consumer_group"

def run_consumer():
    """
    Inicia o consumidor Kafka e orquestra o pipeline ETL para cada mensagem.
    """
    consumer = None
    logger.info("Iniciando o Kafka Consumer...")
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BROKER_URL,
            group_id=CONSUMER_GROUP_ID,
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )
        logger.info(f"Consumidor conectado e escutando o tópico '{TOPIC_NAME}'...")

        # Para cada mensagem realiza um processo de ETL de registro único
        for message in consumer:
            try:
                evento_bruto = message.value
                logger.info(f"Mensagem recebida: {evento_bruto}")

                evento_limpo = clean_validate_single_record(evento_bruto)
                if evento_limpo is None:
                    continue

                pacote_db, evento_db = transform_single_record(evento_limpo)

                load_single_record(pacote_db, evento_db)

            except json.JSONDecodeError:
                logger.error(f"Não foi possível decodificar a mensagem JSON: {message.value}")
            except Exception as e:
                logger.exception(f"Erro inesperado ao processar a mensagem: {e}")

    except KeyboardInterrupt:
        logger.warning("Processo de encerramento iniciado pelo usuário (Ctrl+C).")

    except Exception as e:
        logger.exception(f"Falha crítica no consumidor: {e}")

    finally:
        if consumer:
            logger.info("Fechando conexão do Kafka Consumer...")
            consumer.close()
            logger.info("Consumer encerrado com sucesso.")

if __name__ == "__main__":
    setup_logging()
    run_consumer()