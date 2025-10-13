# Desafio 2 - Proposta de Solução

Este diretório contém a solução para o desafio 1 do processo seletivo da IZE Gestão Empresarial para engenheiro de dados júnior. Desafio esse que consiste em construir uma dashboard que se alimenta das informações coletadas no desafio 1 e também a implementação de uma nova arquitetura focada na trasmissão de informações em tempo real.

## 1. Evolução para uma Arquitetura de Streaming (Tempo Real)

Com a futura mudança do recebimento de dados de arquivos CSV diários para um endpoint de API em tempo real, a arquitetura de processamento em lote (batch) se torna inadequada. Para lidar com um fluxo contínuo de eventos, é proposta uma nova arquitetura de **processamento de streaming**, projetada para ser resiliente, escalável e fornecer dados ao dashboard com latência mínima.

### Diagrama da Nova Arquitetura

O fluxo de dados em tempo real seguiria o seguinte caminho:

```txt
[Endpoint da API] -> [Serviço de Ingestão (Producer)] -> [Apache Kafka (Tópico: `eventos_rastreamento`)] -> [Serviço de Processamento (Consumer)] -> [TimescaleDB] -> [Dashboard (Streamlit)]
```

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

### Adaptações no Modelo de Dados para o TimescaleDB

O modelo lógico com as tabelas `pacotes` e `eventos_rastreamento` permanece perfeitamente válido. No entanto, para aproveitar o poder do TimescaleDB, uma adaptação física é necessária: a tabela `eventos_rastreamento` deve ser convertida em uma **hypertable**.

Uma **hypertable** é uma tabela virtual que o TimescaleDB particiona automaticamente em "pedaços" menores (chunks) com base em uma dimensão, geralmente o tempo. Isso otimiza drasticamente as inserções e as consultas baseadas em períodos de tempo.

As seguintes alterações seriam necessárias no script `init-db/create_tables.sql`:

1.  **Habilitar a Extensão:** O primeiro comando no script deve ser para carregar a extensão do TimescaleDB.
    ```sql
    CREATE EXTENSION IF NOT EXISTS timescaledb;
    ```

2.  **Converter a Tabela em Hypertable:** Após a criação da tabela `eventos_rastreamento`, o seguinte comando deve ser executado para transformá-la em uma hypertable, particionada pela coluna de tempo.
    ```sql
    -- Converte a tabela de eventos em uma hypertable, particionada pela coluna data_evento
    SELECT create_hypertable('eventos_rastreamento', 'data_evento');
    ```
Com essas modificações, a arquitetura estaria pronta para ingerir e analisar dados de rastreamento em tempo real de forma robusta e escalável.
