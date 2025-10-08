CREATE TABLE pacotes (
    id_pacote INT PRIMARY KEY,
    origem VARCHAR(255) NOT NULL,
    destino VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE eventos_rastreamento (
    id_evento SERIAL PRIMARY KEY,
    id_pacote INT NOT NULL,
    status_rastreamento VARCHAR(100) NOT NULL,
    data_evento TIMESTAMP WITH TIME ZONE NOT NULL,

    CONSTRAINT fk_eventos_pacotes
        FOREIGN KEY(id_pacote)
        REFERENCES pacotes(id_pacote)
);

-- Criar um índice para ganho de desempenho em busca de eventos
CREATE INDEX idx_eventos_id_pacote ON eventos_rastreamento(id_pacote);