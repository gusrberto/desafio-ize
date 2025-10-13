# Desafio 2 - Proposta de Solução

Este diretório contém a solução para o desafio 1 do processo seletivo da IZE Gestão Empresarial para engenheiro de dados júnior. Desafio esse que consiste em construir uma dashboard que se alimenta das informações coletadas no desafio 1 e também a implementação de uma nova arquitetura focada na trasmissão de informações em tempo real.

## Tabela de Conteúdos
1.  [Parte 1: Dashboard de Monitoramento com Streamlit](#1-parte-1-dashboard-de-monitoramento-com-streamlit)
2.  [Parte 2: Evolução para Arquitetura de Streaming](#2-parte-2-evolução-para-arquitetura-de-streaming)
3.  [Tecnologias Utilizadas](#3-tecnologias-utilizadas)
4.  [Estrutura do Projeto](#4-estrutura-do-projeto)
5.  [Gerenciamento do Projeto com Kanban](#5-gerenciamento-do-projeto-com-kanban)
6.  [Modelo de Dados para Streaming (TimescaleDB)](#6-modelo-de-dados-para-streaming-timescaledb)
7.  [Queries Principais (KPIs do Dashboard)](#7-queries-principais-kpis-do-dashboard)
8.  [Pré-requisitos](#8-pré-requisitos)
9.  [Como Executar as Soluções do Desafio](#9-como-executar-as-soluções-do-desafio)
10. [Acessando os Bancos de Dados](#10-acessando-os-bancos-de-dados)
11. [Processo de Pensamento](#11-processo-de-pensamento)

## Parte 1: Dashboard de Monitoramento com Streamlit

Para atender à necessidade da equipe de análise de negócios, foi desenvolvido um dashboard web interativo utilizando a biblioteca **Streamlit**. A escolha pelo Streamlit se deu por sua simplicidade e rapidez de desenvolvimento, permitindo a criação de uma solução robusta e focada em dados com código Python puro.

O dashboard se conecta ao banco de dados PostgreSQL populado pelo pipeline do Desafio 1 e exibe os seguintes KPIs:
* **Contagem de Pacotes por Status:** Um gráfico de pizza interativo mostrando a distribuição do status mais recente de todos os pacotes.
* **Tempo Médio de Entrega:** Um card de KPI que calcula e exibe o tempo médio decorrido entre o primeiro evento e o evento de 'ENTREGUE'.
* **Total de Pacotes:** Um card de KPI com a contagem total de pacotes únicos no sistema.

<center>

![Dashboard Streamlit](./docs/dashboard-streamlit.png)
**Figura 1 - Dashboard de Monitoramento de Entregas construído com Streamlit**

</center>

## Parte 2: Evolução para uma Arquitetura de Streaming

Com a futura mudança do recebimento de dados de arquivos CSV diários para um endpoint de API em tempo real, a arquitetura de processamento em lote (batch) se torna inadequada. Para lidar com um fluxo contínuo de eventos, é proposta uma nova arquitetura de **processamento de streaming**, projetada para ser resiliente, escalável e fornecer dados ao dashboard com latência mínima.

### Diagrama da Nova Arquitetura

O fluxo de dados em tempo real seguiria o seguinte caminho:

<center>

![Pipeline Tempo Real](./docs/realtime_diagram.svg)
**Figura 2 - Diagrama das etapas do Pipeline de Streaming em Tempo Real**

</center>

### Descrição e Justificativa dos Componentes

Cada componente foi escolhido para desempenhar um papel específico na garantia de um pipeline robusto e escalável.

#### 1. Serviço de Ingestão (Python Kafka Producer)
* **Papel:** Um microserviço leve e contínuo que consome os dados do endpoint da API assim que são disponibilizados. Sua única responsabilidade é receber cada evento (payload JSON), validá-lo minimamente e publicá-lo como uma mensagem no tópico do Kafka.
* **Justificativa:** Desacopla a fonte de dados (API) do resto do pipeline. Se o processamento ficar lento ou parar, o serviço de ingestão pode continuar recebendo dados e enfileirando-os no Kafka, sem risco de perda.

#### 2. Fila de Mensagens (Apache Kafka)
* **Papel:** Atua como um "buffer" durável e de alta capacidade entre a ingestão e o processamento. Ele armazena os eventos de rastreamento em um log distribuído e à prova de falhas.
* **Justificativa:**
    * **Absorção de Picos (Backpressure):** Se a API enviar uma rajada de eventos, o Kafka os absorve, permitindo que o serviço de processamento os consuma em seu próprio ritmo, sem ser sobrecarregado.
    * **Durabilidade e Garantia de Entrega:** As mensagens são persistidas no disco do Kafka. Se o serviço de processamento cair, as mensagens não são perdidas e podem ser reprocessadas assim que ele voltar a operar.

#### 3. Serviço de Processamento (Python Kafka Consumer)
* **Papel:** Um serviço contínuo que "escuta" o tópico do Kafka. Para cada nova mensagem recebida, ele executa a lógica de negócio: limpeza, validação, transformação (reutilizando os módulos `clean_validate.py` e `transform.py` do Desafio 1) e, por fim, insere os dados no banco de dados.
* **Justificativa:** Isola a lógica de negócio e permite que ela seja escalada de forma independente. Se o fluxo de eventos aumentar, podemos simplesmente iniciar mais instâncias deste consumidor para processar as mensagens em paralelo.

#### 4. Banco de Dados (PostgreSQL com TimescaleDB)
* **Papel:** Armazena os dados de pacotes e eventos para serem consultados pelo dashboard. A substituição do PostgreSQL padrão pela extensão TimescaleDB é crucial.
* **Justificativa:** O PostgreSQL padrão é excelente, mas pode se tornar um gargalo de **escrita (write)** sob um fluxo constante de eventos em tempo real. O **TimescaleDB** é uma extensão que transforma o PostgreSQL em um banco de dados de série temporal de alta performance, projetado especificamente para lidar com milhões de inserções por segundo de forma eficiente, sem degradar a performance de leitura.

## 3. Tecnologias Utilizadas

* **Visualização de Dados:** Streamlit, Plotly Express
* **Sistema de Mensageria:** Apache Kafka, Zookeeper (via Confluent Platform)
* **Banco de Dados de Streaming:** TimescaleDB
* **Interação com Kafka:** `kafka-python`
* **Containerização:** Docker e Docker Compose

## 4. Estrutura do Projeto

O Desafio 2 foi organizado em subdiretórios para separar as duas soluções principais:

```bash
desafio-2
├── dashboard-csv
│   ├── dashboard.py                            # Dashboard para dados em lote
│   ├── src                                     # Funções auxiliares para dashboard em lote
│   │   ├── data.py
│   │   └── utils.py
│   └── .streamlit
│       └── config.toml                         # Arquivo de configuração do streamlit
├── dashboard-realtime
│   ├── consumer.py                             # Serviço que consome o Kafka e carrega no BD
│   ├── dashboard.py                            # Dashboard para dados em tempo real
│   ├── docker-compose.yaml                     # Infraestrutura (TimescaleDB, Kafka, Zookeeper)
│   ├── .env.example                            # Modelo de .env para o Compose
│   ├── etl                                     # Módulos de ETL adaptados para inserção de único registro
│   │   ├── clean_validate.py
│   │   ├── load.py
│   │   └── transform.py
│   ├── init-db
│   │   └── create_tables.sql                   # DDL para TimescaleDB com Hypertable
│   ├── producer.py                             # Script que simula a API e envia para o Kafka
│   ├── src                                     # Funções auxiliares para dashboard em tempo real
│   │   ├── data.py
│   │   └── utils.py
│   └── .streamlit 
│       └── config.toml                         # Arquivo de configuração do streamlit
├── README.md                                   # Documentação do Desafio
└── requirements.txt                            # Dependências do Projeto
```

## 5. Gerenciamento do Projeto com Kanban

Assim como no Desafio 1, o desenvolvimento foi gerenciado utilizando **GitHub Projects** com um quadro Kanban. O desafio foi decomposto em Issues que representavam cada etapa, desde a configuração da infraestrutura até o desenvolvimento dos dashboards e serviços de streaming.

<center>

![Imagem Kanban](./docs/kanban-desafio-2.png)
**Figura 3 - Kanban do projeto no GitProjects com as Issues representadas como tasks**

</center>

**[Você pode visualizar o quadro Kanban finalizado do projeto aqui.](https://github.com/users/gusrberto/projects/2)**

## 6. Modelo de Dados para Streaming (TimescaleDB)

Para otimizar a tabela `eventos_rastreamento` para o TimescaleDB, o schema do desafio 1 foi ajustado:
* A coluna `id_evento` foi removida.
* Uma **chave primária composta `(id_pacote, data_evento)`** foi criada, o que satisfaz a exigência do TimescaleDB de que a coluna de particionamento (`data_evento`) faça parte da chave primária.
* A tabela foi convertida em uma **hypertable**, particionada pela coluna `data_evento`.

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE pacotes (...); -- Permaneceu inalterada

CREATE TABLE eventos_rastreamento (
    id_pacote INT NOT NULL,
    status_rastreamento TEXT NOT NULL,
    data_evento TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (id_pacote, data_evento),
    CONSTRAINT fk_eventos_pacotes
        FOREIGN KEY(id_pacote)
        REFERENCES pacotes(id_pacote)
);

SELECT create_hypertable('eventos_rastreamento', 'data_evento');

CREATE INDEX idx_eventos_id_pacote ON eventos_rastreamento(id_pacote);
```

## 7. Queries Principais (KPIs do Dashboard)

Para alimentar os gráficos e métricas do dashboard, foram desenvolvidas duas queries SQL principais. Elas são projetadas para serem executadas diretamente no banco de dados (PostgreSQL/TimescaleDB), realizando os cálculos complexos de forma otimizada.

### 1. Contagem de Pacotes por Status Atual

Esta query calcula o número de pacotes para cada status, considerando apenas o evento **mais recente** de cada pacote.

```sql
WITH ultimo_evento AS (
    SELECT
        id_pacote,
        status_rastreamento,
        ROW_NUMBER() OVER(PARTITION BY id_pacote ORDER BY data_evento DESC) as rn
    FROM eventos_rastreamento
)
SELECT
    status_rastreamento,
    COUNT(id_pacote) AS total_pacotes
FROM ultimo_evento
WHERE rn = 1
GROUP BY status_rastreamento;
```

* **Como Funciona**:

    1. **O Problema**: A tabela `eventos_rastreamento` contém todo o histórico de um pacote. Uma simples contagem agrupada por status (`GROUP BY status_rastreamento`) contaria o mesmo pacote múltiplas vezes, uma para cada status que ele já teve.

    2. **Solução (Função de Janela)**: Utilizamos uma Common Table Expression (CTE) chamada `ultimo_evento` para pré-filtrar os dados.

        - `PARTITION BY id_pacote`: Agrupa todos os eventos que pertencem ao mesmo pacote.

        - `ORDER BY data_evento DESC`: Dentro de cada grupo de pacote, ordena os eventos do mais novo para o mais antigo.

        - `ROW_NUMBER() ... as rn`: Numera sequencialmente cada evento dentro do seu grupo. Graças à ordenação, o evento mais recente de cada pacote sempre receberá o número `1`.

    3. **Filtragem Final**: A query principal seleciona os dados da CTE e aplica o filtro `WHERE rn = 1`. Isso garante que estamos trabalhando apenas com o último status de cada pacote. A partir daí, um simples `GROUP BY` e `COUNT` nos dá o resultado desejado.

### 2. Tempo Médio de Entrega

Esta query calcula o tempo médio decorrido entre o primeiro evento de um pacote e o seu evento de entrega final.

```sql
WITH entregas_finalizadas AS (
    SELECT
        id_pacote,
        MIN(data_evento) AS data_inicio,
        MAX(CASE WHEN status_rastreamento = 'ENTREGUE' THEN data_evento ELSE NULL END) AS data_entrega
    FROM
        eventos_rastreamento
    GROUP BY
        id_pacote
)
SELECT
    AVG(data_entrega - data_inicio) AS tempo_medio_de_entrega
FROM
    entregas_finalizadas
WHERE
    data_entrega IS NOT NULL;
```

* **Como Funciona**:

    1. **O Problema**: Precisamos encontrar o tempo de início (`MIN(data_evento)`) e o tempo de fim de cada pacote. No entanto, o tempo de fim não é simplesmente o `MAX(data_evento)`, pois um pacote pode ter eventos posteriores à entrega (ex: devolução). O tempo de fim deve ser a data do status `'ENTREGUE'`.

    2. **Solução (Agregação Condicional)**: A CTE `entregas_finalizadas` resolve isso de forma elegante para cada `id_pacote`.

        - `MIN(data_evento) AS data_inicio`: Encontra a data do primeiro evento de um pacote, que consideramos o início do processo de envio.

        - `MAX(CASE WHEN status_rastreamento = 'ENTREGUE' ...)`: Esta é a agregação condicional. Para cada pacote, ela olha todos os seus eventos. Se um evento tem o status `'ENTREGUE'`, ela considera sua data. Caso contrário, ignora. O `MAX` garante que pegaremos a data da última entrega, caso haja mais de uma. Se um pacote nunca foi entregue, o resultado para `data_entrega` será `NULL`.

    3. **Cálculo Final**: A query principal calcula a média (`AVG`) da diferença entre `data_entrega` e `data_inicio`. O filtro `WHERE data_entrega IS NOT NULL` garante que o cálculo seja feito apenas para os pacotes que foram efetivamente entregues, ignorando todos os outros.

## 8. Pré-requisitos

* Git
* Python 3.9+
* Docker
* Docker Compose

## 9. Como Executar as Soluções do Desafio

### Parte 1: Executando a Dashboard em Lote

Esta Dashboard se conecta ao banco de dados criado no **Desafio 1**.

1. **Inicie a Infraestrutura do Desafio 1**:

    ```bash
    cd ../desafio-1/pipeline/
    docker compose -f docker-compose.dev.yaml up
    ```

2. **Instale as Dependências do Desafio 2**:

    ```bash
    cd ../desafio-2/
    pip install -r requirements.txt
    ```

3. **Execute a Dashboard**:

    ```bash
    # A partir da raíz do desafio-2/dashboard-csv
    streamlit run dashboard.py
    ```

### Parte 2: Executando o Pipeline de Streaming e a Dashboard em Tempo Real

1. **Configure o `.env`**: Na pasta `desafio-2/dashboard-realtime/`, crie um arquivo `.env` com base no `./desafio-2/dashboard-realtime/.env.example` e adicione a URL para o TimescaleDB.

    ```ini
    # Exemplo de .env
    POSTGRES_USER=docker
    POSTGRES_PASSWORD=12345
    POSTGRES_DB=realtime_logistica

    TIMESCALE_DATABASE_URL="postgresql://docker:12345@localhost:5434/realtime_logistica"
    ```

2. **Inicie a Infraestrutura de Streaming**:

    ```bash
    # No diretório dashboard-realtime/
    docker compose up --build
    ```

3. **Execute os Componentes (em terminais separados)**:

    * **Terminal 1 (Consumer)**: Inicie o serviço que escuta o Kafka.

    ```bash
    python consumer.py
    ```

    * **Terminal 2 (Dashboard)**: Inicie a dashboard de tempo real.

    ```bash
    # A partir da raíz do desafio-2/dashboard-realtime
    streamlit run dashboard.py
    ```

    * **Terminal 3 (Producer)**: Execute o script que simula a chegada de novos eventos.

    ```bash
    python producer.py
    ```

Observe a dashboard se atualizar automaticamente após a execução do producer.

## 10. Acessando os Bancos de Dados

* **Banco PostgreSQL (Desafio 1)**: Porta `5433`

* **Banco TimescaleDB (Desafio 2)**: Porta `5434`

Use localhost como host e as credenciais do seu `.env` para se conectar via DBeaver (ou similares).

## 11. Processo de Pensamento

Assim como no Desafio 1, o desenvolvimento do desafio foi feito iterativamente, com decisões sendo tomadas para aumentar a robustez e a qualidade do código. O processo de pensamento detalhado para cada etapa está documentado nas descrições dos seguintes PRs (Pull-Requests):

* **PR [#1](https://github.com/gusrberto/desafio-ize/pull/33) - Configuração da Dashboard**: Escolha do Streamlit, desenvolvimento das queries e criação da camada de dados.
* **PR [#2](https://github.com/gusrberto/desafio-ize/pull/34) - Interface da Ambiente**: Implementação da UI com Plotly e componentes nativos do Streamlit.
* **PR [#3](https://github.com/gusrberto/desafio-ize/pull/35) - Design da Arquitetura de Streaming**: Documentação da nova arquitetura com Kafka e TimescaleDB.
* **PR [#4](https://github.com/gusrberto/desafio-ize/pull/36) e [#5](https://github.com/gusrberto/desafio-ize/pull/37) - Implementação da Infraestrutura de Streaming**: Configuração do TimescaleDB e do Kafka via Docker Compose.
* **PR [#6](https://github.com/gusrberto/desafio-ize/pull/38) e [#7](https://github.com/gusrberto/desafio-ize/pull/39) - Desenvolvimento do Producer e Consumer**: Criação dos serviços de ingestão e processamento de eventos.
* **PR [#7](https://github.com/gusrberto/desafio-ize/pull/42) - Integração da Dashboard Real-Time**: Conexão do Streamlit ao pipeline de streaming com atualização automática.