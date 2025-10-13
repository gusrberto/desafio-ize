from datetime import timedelta

def formatar_timedelta(td: timedelta) -> str:
    """
    Converte um objeto timedelta em uma string de data em Português.
    """

    # Extrai o total de dias e o restante dos segundos
    dias = td.days
    segundos_restantes = td.seconds

    # Calcula horas, minutos e segundos a partir do restante
    horas, rem = divmod(segundos_restantes, 3600)
    minutos, segundos = divmod(rem, 60)

    partes = []
    if dias > 0:
        sufixo_dia = "dia" if dias == 1 else "dias"
        partes.append(f"{dias} {sufixo_dia}")

    # Formata o horário como HH:MM:SS
    partes.append(f"{horas:02d}:{minutos:02d}:{segundos:02d}")

    return ", ".join(partes)
