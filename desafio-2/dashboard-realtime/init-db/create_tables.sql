-- Habilita a extensão do TimescaleDB no banco de dados.
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE pacotes (
    id_pacote INT PRIMARY KEY,
    origem TEXT NOT NULL,
    destino TEXT NOT NULL,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE eventos_rastreamento (
    id_pacote INT NOT NULL,
    status_rastreamento TEXT NOT NULL,
    data_evento TIMESTAMP WITH TIME ZONE NOT NULL,

    CONSTRAINT pk_eventos_rastreamento
        PRIMARY KEY (id_pacote, data_evento),

    CONSTRAINT fk_eventos_pacotes
        FOREIGN KEY(id_pacote)
        REFERENCES pacotes(id_pacote)
);

-- Converte a tabela de eventos_rastreamento em uma Hypertable.
-- Particiona a tabela 'eventos_rastreamento' com base na coluna 'data_evento'.
SELECT create_hypertable('eventos_rastreamento', 'data_evento');

-- Índice para otimização de joins com a tabela pacotes.
CREATE INDEX idx_eventos_id_pacote ON eventos_rastreamento(id_pacote);