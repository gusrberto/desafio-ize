import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def clean_validate_single_record(evento: dict) -> dict | None:
    """
    Limpa e valida um único registro de evento.
    Retorna o dicionário limpo ou None se for inválido.
    """
    # Verifica se as chaves essenciais existem
    required_keys = ['id_pacote', 'origem', 'destino', 'status_rastreamento', 'data_atualizacao']
    if not all(key in evento for key in required_keys):
        logger.warning(f"Registro descartado - chaves ausentes: {evento}")
        return None

    try:
        # 2. Limpeza: Remove espaços extras
        evento['origem'] = str(evento['origem']).strip()
        evento['destino'] = str(evento['destino']).strip()
        evento['status_rastreamento'] = str(evento['status_rastreamento']).strip()

        # 3. Validação e Conversão de Tipos
        evento['id_pacote'] = int(evento['id_pacote'])
        evento['data_atualizacao'] = datetime.fromisoformat(evento["data_atualizacao"].replace('Z', '+00:00'))

    except (ValueError, TypeError) as e:
        logger.warning(f"Registro descartado - dados inválidos (tipo ou formato): {evento}. Erro: {e}")
        return None
    
    return evento
