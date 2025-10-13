import json
import logging
import time
from kafka import KafkaProducer

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

def inicializar_producer() -> KafkaProducer | None:
    """
    Tenta criar e retornar uma instância do KafkaProducer.
    Retorna None em caso de falha.
    """

    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=5
        )
        logger.info("Kafka Producer conectado com sucesso")
        return producer
    except Exception as e:
        logger.exception(f"Falha ao se conectar ao Kafka Producer: {e}")
        return None
    
def enviar_evento(producer: KafkaProducer, evento: dict):
    """
    Envia um único evento de rastreamento para o tópico Kafka,
    simulando o comportamento da API.

    Args:
        `producer`: A instância do KafkaProducer.
        `evento`: Um dicionário Python representando o evento JSON.
    """

    try:
        future = producer.send(TOPIC_NAME, value=evento)
        result = future.get(timeout=10) # Espera 10 segundos
        logger.info(f"Evento enviado com sucesso para o tópico '{result.topic}' na partição {result.partition}.")
    except Exception as e:
        logger.exception(f"Falha ao enviar evento para o Kafka: {e}")

if __name__ == "__main__":
    setup_logging()
    logger.info("Iniciando script do produtor de eventos...")

    kafka_producer = inicializar_producer()

    if kafka_producer:
        # Simulando requisições no endpoint da API

        evento_1 = {
            "id_pacote": 1333,
            "origem": "Natal",
            "destino": "Paraíba",
            "status_rastreamento": "AGUARDANDO RETIRADA",
            "data_atualizacao": "2025-10-12T08:15:00Z"
        }
        enviar_evento(kafka_producer, evento_1)

        time.sleep(5)

        evento_2 = {
            "id_pacote": 1411,
            "origem": "Acre",
            "destino": "Rondônia",
            "status_rastreamento": "EXTRAVIADO",
            "data_atualizacao": "2025-10-12T14:30:00Z"
        }
        enviar_evento(kafka_producer, evento_2)
        
        time.sleep(5)

        evento_3 = {
            "id_pacote": 1333,
            "origem": "Natal",
            "destino": "Paraíba",
            "status_rastreamento": "ENTREGUE",
            "data_atualizacao": "2025-10-13T17:40:00Z"
        }
        enviar_evento(kafka_producer, evento_3)

        kafka_producer.flush()
        kafka_producer.close()
        logger.info("Produtor finalizado e todas as mensagens enviadas.")