# Desafio 1 - Proposta de Solução

Este diretório contém a solução para o desafio 1 do processo seletivo da IZE Gestão Empresarial para engenheiro de dados júnior. Desafio esse que consiste em construir um pipeline para processar informações de rastreamento de pacotes a partir de um arquivo CSV.

## Tabela de Conteúdos
1.  [Arquitetura e Solução Proposta](#1-arquitetura-e-solução-proposta)
2.  [Tecnologias Utilizadas](#2-tecnologias-utilizadas)
3.  [Estrutura do Projeto](#3-estrutura-do-projeto)
4.  [Gerenciamento de Projeto com Kanban](#4-gerenciamento-do-projeto-com-kanban)
5.  [Modelo de Dados](#5-modelo-de-dados)
6.  [Pré-requisitos](#6-pré-requisitos)
7.  [Como Executar o Projeto](#7-como-executar-o-projeto)
8.  [Acessando o Banco de Dados](#8-acessando-o-banco-de-dados)
9.  [Processo de Pensamento](#9-processo-de-pensamento)

## 1. Arquitetura e Solução Proposta

### Visão Geral do Pipeline

O pipeline proposto segue o padrão ETL (Extração, Transformação, Carregamento) e é projetado para ser robusto, escalável e automatizado. A solução ingere dados de um arquivo CSV, os processa e armazena em um banco de dados relacional, com a orquestração do fluxo sendo gerenciada pelo Apache Airflow. Todo o ambiente de banco de dados é containerizado com Docker para garantir a portabilidade e facilidade de configuração.

### Fluxo do Pipeline (ETL)

O processo de ETL foi dividido nas seguintes etapas:

1.  **Extração (Extract):** O pipeline é iniciado pela leitura do arquivo `rastreamento.csv`. A fonte de dados é monitorada, e o processo pode ser acionado por agendamento ou pela presença de um novo arquivo.
2. **Limpeza e Validação (Clean & Validate):** Garante a qualidade dos dados, limpando campos de texto, validando e convertendo tipos de dados, e descartando registros inválidos.
3.  **Transformação (Transform):** Os dados brutos do CSV passam por um processo de limpeza e validação. As principais transformações incluem:
    * Conversão da coluna `data_atualizacao` para o formato de `TIMESTAMP`.
    * Limpeza de espaços em branco e padronização de campos de texto.
    * Validação de regras de negócio (ex: `id_pacote` não pode ser nulo).
4.  **Carregamento (Load):** Os dados transformados são carregados em um banco de dados PostgreSQL. A lógica de carregamento separa as informações do pacote (que não se repetem) das informações de evento (o histórico de status), populando duas tabelas distintas para evitar redundância e manter um histórico completo.

<center>

![Pipeline no Airflow](./docs/pipeline-airflow.png)
**Figura 1 - Pipeline do projeto no Apache Airflow**

</center>

## 2. Tecnologias Utilizadas

A stack de tecnologias foi escolhida para atender aos requisitos de robustez, automação e boas práticas de mercado.

* **Linguagem de Programação:** Python 3.9+
    * *Justificativa:* Linguagem padrão para engenharia de dados, com um ecossistema de bibliotecas maduro e robusto.
* **Manipulação de Dados:** Pandas
    * *Justificativa:* Biblioteca poderosa e eficiente para leitura e manipulação de dados tabulares como CSVs.
* **Banco de Dados:** PostgreSQL (via Docker)
    * *Justificativa:* Banco de dados relacional de código aberto, conhecido por sua confiabilidade, robustez e aderência ao padrão SQL. A containerização com Docker facilita a criação de um ambiente de desenvolvimento idêntico ao de produção.
* **Orquestração:** Apache Airflow (via Docker)
    * *Justificativa:* Ferramenta padrão de mercado para orquestração de workflows. Permite agendamento complexo, monitoramento, retentativas automáticas e visualização clara do status dos pipelines. A containerização com Docker é recomendada pela comunidade Airflow como a melhor maneira para rodar tanto em ambientes de desenvolvimento quanto em produção.

## 3. Estrutura do Projeto

A estrutura do projeto foi organizada para separar as responsabilidades, com o ambiente Airflow e o código do pipeline em diretórios distintos, mas gerenciados por um `docker-compose.yml` unificado.

```bash
desafio-1
├── airflow
│   ├── dags
│   │   └── pipeline_rastreamento.py            # Script da DAG do Airflow junto das tasks
│   └── Dockerfile                              
├── docker-compose.yaml                         # Docker Compose para subir o projeto com Airflow
├── .env.example                                # Modelo de .env para o Compose
└── pipeline
    ├── docker-compose.dev.yaml                 # Docker Compose apenas com Banco para pipeline local
    ├── .env.example                            # Modelo de .env para o Compose.dev
    ├── etl
    │   ├── clean_validate.py                   # Script de Limpeza e Validação de Dados
    │   ├── extract.py                          # Script de Extração de Dados
    │   ├── load.py                             # Script de Carregamento de Dados
    │   └── transform.py                        # Script de Transformação de Dados
    ├── init-db
    │   └── create_tables.sql                   # Script DDL do Modelo de Dados
    ├── README.md                               # Documentação do Desafio
    ├── requirements-airflow.txt                # Dependências para Imagem com Airflow
    ├── requirements.txt                        # Dependências para Execução do Projeto Localmente
    └── test_pipeline.py                        # Script para Execução do Pipeline Localmente 
```

## 4. Gerenciamento do Projeto com Kanban

O desenvolvimento deste projeto foi gerenciado utilizando a ferramenta **GitHub Projects**, configurada como um quadro **Kanban** para proporcionar uma visão clara e organizada do fluxo de trabalho.

O desafio foi decomposto em tarefas menores e gerenciáveis, onde cada uma foi registrada como uma **Issue** no GitHub. Essas Issues foram então visualizadas como cartões em um quadro Kanban com três colunas principais, representando os estágios do ciclo de vida de cada tarefa:

* **To Do (A Fazer):** Continha o backlog de todas as tarefas planejadas e prontas para serem iniciadas.
* **In Progress (Em Andamento):** Representava a tarefa que estava sendo ativamente desenvolvida no momento.
* **Done (Concluído):** Agrupava as tarefas finalizadas, cujo Pull Request correspondente já havia sido revisado e mesclado à branch principal.

<center>

![Imagem Kanban](./docs/kanban-gitprojects.png)
**Figura 2 - Kanban do projeto no GitProjects com as Issues representadas como tasks**

</center>

**[Você pode visualizar o quadro Kanban finalizado do projeto aqui.](https://github.com/users/gusrberto/projects/1)**

## 5. Modelo de Dados

Para armazenar os dados de forma eficiente e normalizada, foi projetado um modelo relacional com duas tabelas principais. Esta abordagem evita a redundância de dados e permite consultas eficientes sobre o histórico de um pacote.

* **Tabela `pacotes`**: Armazena as informações estáticas de cada pacote.
* **Tabela `eventos_rastreamento`**: Armazena todo o histórico de eventos de rastreamento para cada pacote, estabelecendo uma relação de `1:N` com a tabela `pacotes`. Além de possuir uma `UNIQUE` em `(id_pacote, data_evento)` para garantir idempotência.
* **Adição de índice ganho em desempenho**: Para garantir consultas rápidas ao buscar o histórico completo de um pacote (`WHERE id_pacote = ...`), um índice será criado na coluna `id_pacote` desta tabela.

```sql
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
        REFERENCES pacotes(id_pacote),
    CONSTRAINT uq_pacote_data_evento
        UNIQUE (id_pacote, data_evento)
);

-- Criar um índice para ganho de desempenho em busca de eventos
CREATE INDEX idx_eventos_id_pacote ON eventos_rastreamento(id_pacote);
```

## 6. Pré-requisitos

* Git
* Python 3.9+
* Docker
* Docker Compose

## 7. Como Executar o Projeto

1. **Clone o Repositório**:

    ```bash
    git clone https://github.com/gusrberto/desafio-ize
    cd desafio-ize/
    ```

2. **Configure as Variáveis de Ambiente**:

    Copie o arquivo de exemplo `.env.example` e preencha as variáveis no novo arquivo `.env`.

    **ATENÇÃO**: Há duas `.env` nesse projeto, uma para o `docker-compose.yaml` que executa o pipeline pelo Airflow (está no diretório raíz desafio-1/ do projeto), e outra para o `docker-compose.dev.yaml` que apenas sobe o banco de dados para executar o pipeline localmente.

    ```bash
    # No diretório desafio-1/
    cp .env.example .env
    cp pipeline/.env.example pipeline/.env
    ```

    Exemplo de conteúdo para a `.env` que executa o Airflow:
    ```ini
    POSTGRES_USER=docker
    POSTGRES_PASSWORD=12345
    POSTGRES_DB=logistica_pacotes

    AIRFLOW_DATABASE_URL="postgresql+psycopg2://docker:12345@pipeline_db:5432/logistica_pacotes"

    AIRFLOW_UID=1000
    ```

    Exemplo de conteúdo para a `pipeline/.env` que executa o pipeline local:
    ```ini
    POSTGRES_USER=docker
    POSTGRES_PASSWORD=12345
    POSTGRES_DB=logistica_pacotes

    LOCAL_DATABASE_URL="postgresql://docker:12345@localhost:5432/logistica_pacotes"
    ```

3. **Inicie o Ambiente**:

    1. **Pipeline Airflow**:

        Execute o Docker Compose a partir da raiz do projeto. Este comando irá construir a imagem customizada do Airflow, criar os volumes e iniciar todos os serviços.

        ```bash
        docker compose up --build
        ```

    2. **Acesse o Airflow**:

        Após alguns minutos para a inicialização completa, acesse a interface do Airflow em http://localhost:8080.

        * **Usuário**: `airflow`
        * **Senha**: `airflow`

    3. **Configure a Conexão com o Banco**:

        Na interface do Airflow, na barra lateral vá na seção **Admin->Connections->Add Connection**.

        Preencha com as seguintes informações (seguindo o exemplo da `.env` anterior):
      
        - Connection ID: `postgres_pipeline_db`
        - Connection type: `postgres`
        - Host: `pipeline_db`
        - Login: `docker`
        - Password: `12345`
        - Port: `5432`
        - Schema: `logistica_pacotes`

    4. **Execute a DAG**:

        Na UI do Airflow, encontre a DAG chamada `dag_pipeline_rastreamento`, despause-a no botão de toggle e clique no botão "Play" para disparar uma execução manual.

    **Execução Pipeline Local**:

    Para executar o pipeline localmente sem o Airflow:
    
    - Crie e ative um ambiente virtual python com:
        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```
    - Instale as dependências com:
        ```bash
        pip install -r pipeline/requirements.txt
        ```
    - Suba o contâiner apenas com o banco de dados com `docker-compose.dev.yaml` dentro do diretório `pipeline/` com:
        ```bash
        docker compose -f pipeline/docker-compose.dev.yaml up --build
        ```
    - Execute o script do pipeline:
        ```bash
        python pipeline/test_pipeline.py
        ```

## 8. Acessando o Banco de Dados

É possível se conectar ao banco de dados da aplicação (onde os dados do pipeline são salvos) usando uma ferramenta como DBeaver ou pgAdmin com as seguintes configurações:

- **Host**: `localhost`

- **Porta**: `5433` (mapeada no `docker-compose.yml` e no `docker-compose.dev.yaml`)

- **Banco de Dados**: `logistica_pacotes`

- **Usuário**: `docker`

- **Senha**: `12345` (configurada no `.env`)

## 9. Processo de Pensamento

O desenvolvimento do desafio foi feito iterativamente, com decisões sendo tomadas para aumentar a robustez e a qualidade do código. O processo de pensamento detalhado para cada etapa está documentado nas descrições dos seguintes PRs (Pull-Requests):

* **PR [#1](https://github.com/gusrberto/desafio-ize/pull/12) - Análise e Esboço da Solução Técnica**: Definição da arquitetura inicial, stack de tecnologias e schema inicial do banco.
* **PR [#2](https://github.com/gusrberto/desafio-ize/pull/13) - Configuração do Ambiente**: Estruturação do projeto com `venv` e `requirements.txt`.
* **PR [#3](https://github.com/gusrberto/desafio-ize/pull/14) - Script DDL do Banco**: Implementação do schema SQL, incluindo chaves, índices e constraints.
* **PR [#4](https://github.com/gusrberto/desafio-ize/pull/15) - Containerização com Docker**: Automatização do setup do banco de dados com Docker Compose.
* **PR [#5](https://github.com/gusrberto/desafio-ize/pull/16) e [#6](https://github.com/gusrberto/desafio-ize/pull/19) - Implementação do ETL**: Desenvolvimento dos módulos `extract`, `clean_validate`, `transform` e `load`, com lógicas de idempotência e tratamento de erros.
* **PR [#7](https://github.com/gusrberto/desafio-ize/pull/20) - Adição da Biblioteca Logging**: Substituição de até então prints no código pelo uso da biblioteca `logging`, trazendo um log consistente e padronizado para o projeto.
* **PR [#8](https://github.com/gusrberto/desafio-ize/pull/21) - Orquestação com Airflow**: Integração do pipeline em uma DAG modular com tasks no ambiente Airflow.