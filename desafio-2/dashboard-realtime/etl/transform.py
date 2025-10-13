from typing import Tuple

def transform_single_record(evento_limpo: dict) -> Tuple[dict, dict]:
    """
    Transforma um único evento limpo em dois dicionários, um para cada
    tabela de destino (`pacotes` e `eventos_rastreamento`).
    """
    # Dicionário para a tabela 'pacotes'
    pacote_db = {
        "id_pacote": evento_limpo["id_pacote"],
        "origem": evento_limpo["origem"],
        "destino": evento_limpo["destino"]
    }
    
    # Dicionário para a tabela 'eventos_rastreamento'
    evento_db = {
        "id_pacote": evento_limpo["id_pacote"],
        "status_rastreamento": evento_limpo["status_rastreamento"],
        "data_evento": evento_limpo["data_atualizacao"]
    }

    return pacote_db, evento_db
