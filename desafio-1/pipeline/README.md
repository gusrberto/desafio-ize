# Desafio 1 - Proposta de Solução

Este diretório contém a solução para o desafio 1 do processo seletivo da IZE Gestão Empresarial para engenheiro de dados júnior. Desafio esse que consiste em construir um pipeline para processar informações de rastreamento de pacotes a partir de um arquivo CSV.

## 1. Arquitetura e Solução Proposta

Esta seção documenta o planejamento e o design da solução, correspondendo aos entregáveis da [**Issue #1**](https://github.com/gusrberto/desafio-ize/issues/1).

### Visão Geral do Pipeline

O pipeline proposto segue o padrão ETL (Extração, Transformação, Carregamento) e é projetado para ser robusto, escalável e automatizado. A solução ingere dados de um arquivo CSV, os processa e armazena em um banco de dados relacional, com a orquestração do fluxo sendo gerenciada pelo Apache Airflow. Todo o ambiente de banco de dados é containerizado com Docker para garantir a portabilidade e facilidade de configuração.

### Fluxo do Pipeline (ETL)

O processo de ETL foi dividido nas seguintes etapas:

1.  **Extração (Extract):** O pipeline é iniciado pela leitura do arquivo `rastreamento.csv`. A fonte de dados é monitorada, e o processo pode ser acionado por agendamento ou pela presença de um novo arquivo.
2.  **Transformação (Transform):** Os dados brutos do CSV passam por um processo de limpeza e validação. As principais transformações incluem:
    * Conversão da coluna `data_atualizacao` para o formato de `TIMESTAMP`.
    * Limpeza de espaços em branco e padronização de campos de texto.
    * Validação de regras de negócio (ex: `id_pacote` não pode ser nulo).
3.  **Carregamento (Load):** Os dados transformados são carregados em um banco de dados PostgreSQL. A lógica de carregamento separa as informações do pacote (que não se repetem) das informações de evento (o histórico de status), populando duas tabelas distintas para evitar redundância e manter um histórico completo.

### Tecnologias Utilizadas

A stack de tecnologias foi escolhida para atender aos requisitos de robustez, automação e boas práticas de mercado.

* **Linguagem de Programação:** Python 3.12+
    * *Justificativa:* Linguagem padrão para engenharia de dados, com um ecossistema de bibliotecas maduro e robusto.
* **Manipulação de Dados:** Pandas
    * *Justificativa:* Biblioteca poderosa e eficiente para leitura e manipulação de dados tabulares como CSVs.
* **Banco de Dados:** PostgreSQL (via Docker)
    * *Justificativa:* Banco de dados relacional de código aberto, conhecido por sua confiabilidade, robustez e aderência ao padrão SQL. A containerização com Docker facilita a criação de um ambiente de desenvolvimento idêntico ao de produção.
* **Orquestração:** Apache Airflow (via Docker)
    * *Justificativa:* Ferramenta padrão de mercado para orquestração de workflows. Permite agendamento complexo, monitoramento, retentativas automáticas e visualização clara do status dos pipelines. A containerização com Docker é recomendada pela comunidade Airflow como a melhor maneira para rodar tanto em ambientes de desenvolvimento quanto em produção.

## 2. Modelo de Dados

Para armazenar os dados de forma eficiente e normalizada, foi projetado um modelo relacional com duas tabelas principais. Esta abordagem evita a redundância de dados e permite consultas eficientes sobre o histórico de um pacote.

### Tabela: `pacotes`

Armazena as informações estáticas de cada pacote.

```sql
CREATE TABLE pacotes (
    id_pacote INT PRIMARY KEY,
    origem VARCHAR(255) NOT NULL,
    destino VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `eventos_rastreamento`

Armazena todo o histórico de eventos de rastreamento para cada pacote, estabelecendo uma relação de `1:N` com a tabela `pacotes`.

```sql
CREATE TABLE eventos_rastreamento (
    id_evento SERIAL PRIMARY KEY,
    id_pacote INT NOT NULL,
    status_rastreamento VARCHAR(100) NOT NULL,
    data_evento TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT fk_pacote
        FOREIGN KEY(id_pacote)
        REFERENCES Pacotes(id_pacote)
);
```

* **Adição de índice ganho em desempenho**: Para garantir consultas rápidas ao buscar o histórico completo de um pacote (`WHERE id_pacote = ...`), um índice será criado na coluna `id_pacote` desta tabela. A implementação do índice faz parte da [Issue #3](https://github.com/gusrberto/desafio-ize/issues/3).