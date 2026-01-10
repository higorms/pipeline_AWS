# B3 Stocks Data Pipeline

<img alt="Static Badge" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/AWS_Lambda-FF9900?logo=awslambda&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/AWS_Glue-8C4FFF?logo=amazonaws&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/Amazon_S3-569A31?logo=amazons3&logoColor=white"> 

> Pipeline de Engenharia de Dados Serverless na AWS para processamento automatizado de dados históricos de ações da B3, com cálculo de indicadores técnicos e disponibilização para análise via SQL.

## 1. Visão Geral

Este projeto implementa um **pipeline de dados completamente serverless e orientado a eventos** na AWS, projetado para ingerir, processar e disponibilizar dados históricos de ações negociadas na B3 (Bolsa de Valores Brasileira).

### Objetivos do Projeto:
- ✅ **Ingestão Automatizada**: Extração diária de dados de ações via yfinance
- ✅ **Processamento Inteligente**: Cálculo de indicadores técnicos (Média Móvel 7d e Volume Acumulado)
- ✅ **Arquitetura Orientada a Eventos**: Processamento disparado automaticamente ao detectar novos dados
- ✅ **Baixo Custo**: Utilização de serviços serverless (sem servidores ociosos)
- ✅ **Alta Escalabilidade**: Arquitetura elástica que se adapta ao volume de dados
- ✅ **Consulta Analítica**: Dados disponíveis via SQL no Amazon Athena

### Diferenciais Técnicos:
- 🚀 **Near Real-Time**: Processamento iniciado instantaneamente ao chegar novo arquivo
- 💰 **Custo-Eficiência**: Python Shell no Glue (0.0625 DPU) em vez de cluster Spark
- 🎯 **Idempotência**: Lógica inteligente previne duplicação de dados
- 📊 **Particionamento Otimizado**: Padrão Hive para redução de custos de leitura
- 🔒 **Segurança**: IAM Roles com princípio do menor privilégio

Autores: Higor Menezes e Narcélio Filho

Versão: 1.0.0

## 2. Arquitetura da Solução

### 2.1. Visão Geral do Fluxo

```
                    📊 PIPELINE DE DADOS - ARQUITETURA EVENT-DRIVEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   🤖 INGESTÃO         📦 ARMAZENAMENTO      ⚡ ORQUESTRAÇÃO     🔄 PROCESSAMENTO      💾 DADOS REFINADOS
  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │             │      │              │      │              │      │              │      │              │
  │  Lambda     │──┬─▶│   S3 Raw     │──┬──▶│   Lambda     │──┬─▶│  AWS Glue    │──┬──▶│ S3 Refined   │
  │  Scraper    │  │   │              │  │   │   Trigger    │  │   │   ETL Job    │  │   │              │
  │             │  │   │  (Parquet)   │  │   │              │  │   │  (Python)    │  │   │  (Parquet)   │
  └─────────────┘  │   └──────────────┘  │   └──────────────┘  │   └──────────────┘  │   └──────────────┘
                   │                     │                     │                     │
      yfinance     │   Particionamento   │   S3 Event          │   Pandas +          │   Particionamento
      API Yahoo    │   Hive Style        │   Notification      │   awswrangler       │   por Data/Ação
                   │                     │                     │                     │
                   └─────────────────────┘                     └─────────────────────┘
                     📂 year=YYYY/                               🧮 Indicadores:
                        month=MM/                                  • Média Móvel 7d
                        day=DD/                                    • Volume Acumulado
                                                                                    │
                                                                                    │
                                                                                    ▼
                                                                          ┌──────────────────┐
                                                                          │                  │
                                                                          │  📈 Athena       │
                                                                          │  (SQL Analytics) │
                                                                          │                  │
                                                                          └──────────────────┘
                                                                                   │
                                                                                   │
                                                                                   |
                                                                                   │                         
                                                                                   ▼                          
                                                                              Consumidores
```

**Fluxo de Dados:**
1. 🤖 **Lambda Scraper** extrai dados diários da B3 via yfinance
2. 📦 **S3 Raw** armazena dados brutos em formato Parquet particionado
3. ⚡ **Lambda Trigger** detecta novo arquivo e dispara processamento automaticamente
4. 🔄 **AWS Glue** processa dados, calcula indicadores técnicos e grava em S3 Refined
5. 💾 **S3 Refined** armazena dados processados e catalogados no Glue Data Catalog
6. 📈 **Athena** permite consultas SQL para análise e consumo dos dados

### 2.2. Componentes Principais

| Componente | Tecnologia | Função |
|------------|------------|---------|
| **Scraper/Ingestão** | AWS Lambda + yfinance | Extração diária de dados da B3 |
| **Data Lake (Raw)** | Amazon S3 + Parquet | Armazenamento de dados brutos particionados |
| **Orquestração** | AWS Lambda + S3 Events | Detecção e disparo automático de processamento |
| **ETL** | AWS Glue (Python Shell) | Cálculo de indicadores e transformações |
| **Data Lake (Refined)** | Amazon S3 + Parquet | Dados processados e catalogados |
| **Catálogo** | AWS Glue Data Catalog | Metadados e schema das tabelas |
| **Análise** | Amazon Athena | Consultas SQL sobre os dados |

## 3. Arquitetura Detalhada (Camadas)

### 3.1. Camada de Domínio (Domain Layer)

Implementa os conceitos centrais do negócio:

```
src/
├── domain/
│   ├── entities/
│   │   └── (entidades de negócio)
│   └── repositories/
│       ├── data_source_repository.py    # Protocol para fontes de dados
│       └── storage_repository.py        # Protocol para armazenamento
```

**Princípios Aplicados:**
- **Dependency Inversion**: Use cases dependem de abstrações (Protocols)
- **Clean Architecture**: Lógica de negócio independente de infraestrutura

### 3.2. Camada de Aplicação (Application Layer)

Casos de uso que orquestram a lógica de negócio:

```
src/
├── application/
│   └── use_cases/
│       ├── extract_b3_data.py           # Extração de dados
│       └── upload_parquet_to_s3.py      # Upload para S3
```

**Casos de Uso:**
- `ExtractB3DataUseCase`: Orquestra a extração de múltiplos símbolos
- `UploadParquetToS3UseCase`: Gerencia upload com particionamento Hive

### 3.3. Camada de Infraestrutura (Infrastructure Layer)

Implementações concretas dos protocolos:

```
src/
├── infrastructure/
│   ├── data_sources/
│   │   ├── b3_data_source.py            # Interface genérica
│   │   └── yfinance_data_source.py      # Implementação yfinance
│   └── storage/
│       └── s3_storage_repository.py     # Implementação S3
```

### 3.4. Camada de Interface (Interface Layer)

```
src/
├── main.py                              # Entry point (Lambda Handler)
└── config/
    ├── logging_config.py                # Configuração de logs
    └── symbols_loader.py                # Carregamento de símbolos
```

## 4. Pipeline de Dados (Detalhamento)

### 4.1. Ingestão e Organização (Raw Layer)

**Armazenamento:** Amazon S3 (`fiap-mlet-finance`)

**Formato:** Arquivos Parquet (colunar, comprimido e eficiente)

**Estratégia de Particionamento (Hive Partitioning):**
```
s3://fiap-mlet-finance/raw/
├── year=2026/
│   ├── month=01/
│   │   ├── day=10/
│   │   │   ├── stocks_1736534400.parquet
│   │   │   └── stocks_1736541600.parquet
│   │   └── day=11/
│   │       └── stocks_1736620800.parquet
```

**Benefícios:**
- ✅ Otimização de leitura (partition pruning)
- ✅ Redução de custos (apenas partições relevantes são lidas)
- ✅ Organização temporal clara

**Estrutura dos Dados Brutos:**
```python
{
    'symbol': 'PETR4.SA',      # Código da ação
    'date': '2026-01-10',      # Data do pregão
    'open': 38.50,             # Preço de abertura
    'high': 39.20,             # Preço máximo
    'low': 38.30,              # Preço mínimo
    'close': 38.95,            # Preço de fechamento
    'volume': 15234500         # Volume negociado
}
```

### 4.2. Orquestração Orientada a Eventos (Trigger)

**Serviço:** AWS Lambda (`glue_trigger.py`)

**Gatilho:** S3 Event Notification (`s3:ObjectCreated:Put`)

**Fluxo de Execução:**
```python
1. Novo arquivo → s3://bucket/raw/year=2026/month=01/day=10/stocks_*.parquet
2. S3 emite evento → Lambda (notificação instantânea)
3. Lambda extrai data via regex → "2026-01-10"
4. Lambda inicia Glue Job → passa argumento --DATA_PROCESSAMENTO=2026-01-10
```

**Código Simplificado:**
```python
def lambda_handler(event, context):
    # Extrai chave do arquivo do evento S3
    key = event['Records'][0]['s3']['object']['key']
    
    # Regex para extrair data da estrutura Hive
    match = re.search(r'year=(\d+)/month=(\d+)/day=(\d+)', key)
    data_processamento = f"{year}-{month}-{day}"
    
    # Dispara Glue Job
    glue_client.start_job_run(
        JobName='stocks_resume',
        Arguments={'--DATA_PROCESSAMENTO': data_processamento}
    )
```

**Benefícios:**
- ⚡ Processamento near real-time
- 💵 Sem custos de polling (verificação periódica)
- 🔄 Escalável automaticamente

### 4.3. Processamento e Transformação (ETL Layer)

**Serviço:** AWS Glue Python Shell (3.9)

**Engine:** Pandas + awswrangler

**Por que Python Shell em vez de Spark?**
- ✅ 16x mais barato (0.0625 DPU vs 1 DPU)
- ✅ Startup mais rápido (segundos vs minutos)
- ✅ Suficiente para o volume de dados (~MB/dia)

**Lógica de Negócio Inteligente:**

#### 4.3.1. Leitura Janelada (7 dias)

O cálculo da **Média Móvel de 7 dias** requer histórico. A solução:

```python
# Para processar 2026-01-10, lê dados de 2026-01-04 até 2026-01-10
caminhos_leitura = []
for i in range(7):
    d = data_ref - timedelta(days=i)
    path = f"s3://bucket/raw/year={d.year}/month={d.month:02d}/day={d.day:02d}/"
    caminhos_leitura.append(path)

# Lê todos os arquivos dos últimos 7 dias
df = wr.s3.read_parquet(path=arquivos_encontrados)
```

**Tratamento de Exceções:**
- Pastas inexistentes (feriados/fins de semana) são ignoradas
- Se nenhum arquivo for encontrado, job termina com sucesso (não é erro)

#### 4.3.2. Normalização de Tipos

```python
# Conversão robusta de datas
df['data_pregao'] = pd.to_datetime(
    df['date'].astype(str).str.strip()
).dt.normalize()

# Ordenação obrigatória para cálculos temporais
df.sort_values(by=['codigo_acao', 'data_pregao'], inplace=True)
```

#### 4.3.3. Cálculo de Indicadores Técnicos

**Média Móvel de 7 Dias:**
```python
df['media_movel_7d'] = (
    df.groupby('codigo_acao')['preco_fechamento']
    .rolling(window=7, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)
```

**Volume Acumulado:**
```python
df['volume_acumulado'] = (
    df.groupby('codigo_acao')['volume_negociado']
    .cumsum()
)
```

#### 4.3.4. Filtro de Output (Idempotência)

**Problema:** Ao ler 7 dias de dados, processamos histórico desnecessário.

**Solução:**
```python
# Identifica a data mais recente nos dados
data_maxima = df['data_pregao'].max()

# Mantém apenas o dia mais novo (D)
df_final = df[df['data_pregao'] == data_maxima].copy()
```

**Benefício:** Garante que apenas dados novos sejam gravados, mesmo em reprocessamentos.

### 4.4. Armazenamento Refinado e Catalogação

**Destino:** `s3://fiap-mlet-finance/refined/`

**Catalogação Automática:**
```python
wr.s3.to_parquet(
    df=df_final,
    path=f"s3://{bucket_name}/refined/",
    dataset=True,                           # Habilita particionamento
    mode="overwrite_partitions",            # Substitui apenas partições afetadas
    partition_cols=["data_pregao", "codigo_acao"],
    database="fiap_stocks_db",              # Glue Data Catalog
    table="stocks_resume",
    compression="snappy"
)
```

**Schema da Tabela `stocks_resume`:**
```sql
CREATE EXTERNAL TABLE fiap_stocks_db.stocks_resume (
    preco_abertura DOUBLE,
    preco_fechamento DOUBLE,
    alta_preco DOUBLE,
    baixa_preco DOUBLE,
    volume_negociado BIGINT,
    media_movel_7d DOUBLE,          -- Indicador calculado
    volume_acumulado BIGINT          -- Indicador calculado
)
PARTITIONED BY (
    data_pregao DATE,
    codigo_acao STRING
)
STORED AS PARQUET
LOCATION 's3://fiap-mlet-finance/refined/'
```

### 4.5. Consumo e Analytics

**Serviço:** Amazon Athena (SQL sobre S3)

**Exemplos de Consultas:**

```sql
-- Top 10 ações por volume no dia 10/01/2026
SELECT 
    codigo_acao,
    preco_fechamento,
    volume_negociado,
    media_movel_7d
FROM fiap_stocks_db.stocks_resume
WHERE data_pregao = DATE '2026-01-10'
ORDER BY volume_negociado DESC
LIMIT 10;

-- Evolução da Petrobras nos últimos 7 dias
SELECT 
    data_pregao,
    preco_fechamento,
    media_movel_7d,
    volume_acumulado
FROM fiap_stocks_db.stocks_resume
WHERE codigo_acao = 'PETR4.SA'
    AND data_pregao >= DATE '2026-01-04'
ORDER BY data_pregao;

-- Análise de volatilidade (amplitude diária)
SELECT 
    codigo_acao,
    data_pregao,
    (alta_preco - baixa_preco) / baixa_preco * 100 AS volatilidade_pct
FROM fiap_stocks_db.stocks_resume
WHERE data_pregao = DATE '2026-01-10'
ORDER BY volatilidade_pct DESC
LIMIT 20;
```

## 5. Instalação e Configuração

### 5.1. Pré-requisitos

- Python 3.13+
- Poetry (gerenciador de dependências)
- Conta AWS com permissões para Lambda, S3, Glue e Athena
- AWS CLI configurado

### 5.2. Instalação Local

```powershell
# Clone o repositório
git clone <repository-url>
cd pipeline_fase02

# Instale as dependências
poetry install

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 5.3. Configuração (.env)

```bash
# AWS Configuration
AWS_REGION=região_da_aws
AWS_S3_BUCKET_NAME=nome_do_bucket

# Logging
LOG_LEVEL=INFO

# Opcionais (para desenvolvimento local)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 5.4. Arquivo de Símbolos

Edite `src/resources/stocks.csv` com as ações desejadas:

```csv
symbol
PETR4.SA
VALE3.SA
ITUB4.SA
BBDC4.SA
ABEV3.SA
```

## 6. Execução

### 6.1. Execução Local (Desenvolvimento)

```powershell
# Ativa o ambiente virtual
poetry shell

# Executa o scraper localmente
poetry run python src/main.py
```

**Comportamento:**
- Extrai dados do último dia útil
- Faz upload para S3 com particionamento Hive
- Loga todas as operações

### 6.2. Execução na AWS (Produção)

#### Deploy do Lambda Scraper

```powershell
# Build da imagem Docker
docker build -t financial-scraping-fiap:latest .

# Tag para ECR
docker tag financial-scraping-fiap:latest <AWS_ID>.dkr.ecr.us-east-1.amazonaws.com/financial-scraping-fiap:latest

# Push para ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ID>.dkr.ecr.us-east-1.amazonaws.com
docker push <AWS_ID>.dkr.ecr.us-east-1.amazonaws.com/financial-scraping-fiap:latest

# Atualizar função Lambda
aws lambda update-function-code \
    --function-name financial-scraping-fiap \
    --image-uri <AWS_ID>.dkr.ecr.us-east-1.amazonaws.com/financial-scraping-fiap:latest
```

#### Deploy do Glue Job

```powershell
# Upload do script ETL para S3
aws s3 cp scripts_aws/glue_etl.py s3://fiap-mlet-finance/scripts/glue_etl.py

# Criar Glue Job (via Console ou CLI)
aws glue create-job \
    --name stocks_resume \
    --role GlueServiceRole \
    --command '{"Name": "pythonshell", "ScriptLocation": "s3://fiap-mlet-finance/scripts/glue_etl.py", "PythonVersion": "3.9"}' \
    --default-arguments '{"--extra-py-files": "", "--library-set": "analytics"}' \
    --max-capacity 0.0625
```

#### Configurar S3 Event Trigger

```powershell
# Deploy da Lambda de trigger
cd scripts_aws
zip -r glue_trigger.zip glue_trigger.py

aws lambda create-function \
    --function-name glue-trigger-stocks \
    --runtime python3.13 \
    --role LambdaS3TriggerRole \
    --handler glue_trigger.lambda_handler \
    --zip-file fileb://glue_trigger.zip \
    --environment Variables="{GLUE_JOB_NAME=stocks_resume}"

# Adicionar permissão para S3 invocar Lambda
aws lambda add-permission \
    --function-name glue-trigger-stocks \
    --statement-id s3-invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::fiap-mlet-finance

# Configurar notificação no bucket S3 (via Console)
```

### 6.3. Agendamento Automático (EventBridge)

```json
// Regra para executar diariamente às 19h (horário de Brasília)
{
  "name": "daily-stock-scraper",
  "schedule": "cron(0 22 * * ? *)",
  "target": {
    "arn": "arn:aws:lambda:us-east-1:848776072486:function:financial-scraping-fiap"
  }
}
```

## 7. Estrutura do Repositório

```
pipeline_fase02/
│
├── src/                                 # Código-fonte principal
│   ├── main.py                          # Entry point (Lambda Handler)
│   │
│   ├── application/                     # Casos de uso
│   │   └── use_cases/
│   │       ├── extract_b3_data.py       # Extração de dados
│   │       └── upload_parquet_to_s3.py  # Upload para S3
│   │
│   ├── config/                          # Configurações
│   │   ├── logging_config.py            # Setup de logs
│   │   └── symbols_loader.py            # Carregamento de símbolos
│   │
│   ├── domain/                          # Entidades e protocolos
│   │   ├── entities/
│   │   └── repositories/
│   │       ├── data_source_repository.py
│   │       └── storage_repository.py
│   │
│   ├── infrastructure/                  # Implementações concretas
│   │   ├── data_sources/
│   │   │   ├── b3_data_source.py
│   │   │   └── yfinance_data_source.py
│   │   └── storage/
│   │       └── s3_storage_repository.py
│   │
│   └── resources/
│       └── stocks.csv                   # Lista de símbolos
│
├── scripts_aws/                         # Scripts AWS
│   ├── glue_etl.py                      # Job Glue (ETL)
│   └── glue_trigger.py                  # Lambda trigger
│
├── pyproject.toml                       # Dependências (Poetry)
├── Dockerfile                           # Containerização (Lambda)
├── README.md                            # Este arquivo
├── resumo.txt                           # Resumo executivo
└── SUMARIO.md                           # Sumário do projeto
```

## 8. Destaques Técnicos e Decisões de Design

### 8.1. Clean Architecture

O projeto segue os princípios da **Clean Architecture**:

```
┌─────────────────────────────────────────────────────┐
│              Interface Layer (main.py)              │
│                   ↓ depends on                      │
│            Application Layer (use_cases)            │
│                   ↓ depends on                      │
│             Domain Layer (protocols)                │
│                   ↑ implemented by                  │
│         Infrastructure Layer (implementations)      │
└─────────────────────────────────────────────────────┘
```

**Benefícios:**
- ✅ **Testabilidade**: Casos de uso testáveis isoladamente
- ✅ **Manutenibilidade**: Mudanças isoladas por camada
- ✅ **Flexibilidade**: Fácil trocar yfinance por outra fonte
- ✅ **Independência**: Lógica de negócio não depende de frameworks

### 8.2. Dependency Injection

```python
# Configuração das dependências (main.py)
data_source = YFinanceDataSource()              # Implementação concreta
storage_repository = S3StorageRepository()      # Implementação concreta

extract_use_case = ExtractB3DataUseCase(data_source)         # Injeta dependência
upload_use_case = UploadParquetToS3UseCase(storage_repository)  # Injeta dependência

# Uso no caso de uso
df = extract_use_case.execute(symbols, start_date, end_date)
```

### 8.3. Custo-Eficiência

**Comparação Python Shell vs Spark:**

| Métrica | Python Shell | Spark Cluster |
|---------|--------------|---------------|
| **DPUs** | 0.0625 | 2 (mínimo) |
| **Custo/hora** | ~$0.04 | ~$0.88 |
| **Startup** | 10-20s | 2-5min |
| **Adequado para** | < 100 MB | > 1 GB |

**Economia:** ~95% de redução de custos para este volume de dados.

### 8.4. Robustez de Datas

O pipeline trata cenários reais do mercado financeiro:

```python
# Cenário 1: Processamento em D+1
# Arquivo chega segunda-feira com dados de sexta
# ✅ Filtro baseado em max(data) garante gravação correta

# Cenário 2: Feriados
# Pastas não existem → ignoradas gracefully
# ✅ Job não falha, apenas avisa no log

# Cenário 3: Reprocessamento
# Executar job novamente para mesma data
# ✅ mode="overwrite_partitions" substitui apenas partição afetada
```

### 8.5. Segurança IAM

**Roles criadas com mínimo privilégio:**

```json
// Lambda Scraper Role
{
  "Effect": "Allow",
  "Action": ["s3:PutObject"],
  "Resource": "arn:aws:s3:::fiap-mlet-finance/raw/*"
}

// Lambda Trigger Role
{
  "Effect": "Allow",
  "Action": ["glue:StartJobRun"],
  "Resource": "arn:aws:glue:*:*:job/stocks_resume"
}

// Glue Job Role
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": [
    "arn:aws:s3:::fiap-mlet-finance/raw/*",
    "arn:aws:s3:::fiap-mlet-finance/refined/*"
  ]
}
```

## 9. Tecnologias Utilizadas

| Categoria | Tecnologia | Versão | Finalidade |
|-----------|------------|--------|------------|
| **Linguagem** | Python | 3.13 | Desenvolvimento principal |
| **Gerenciamento de Dependências** | Poetry | 1.8+ | Gerenciamento de pacotes |
| **Containerização** | Docker | - | Empacotamento Lambda |
| **Extração de Dados** | yfinance | 0.2.0+ | API Yahoo Finance |
| **Processamento** | Pandas | 2.0.0+ | Manipulação de DataFrames |
| **Serialização** | fastparquet | 2024.11+ | Leitura/escrita Parquet |
| **AWS SDK** | boto3 | 1.42+ | Interação com serviços AWS |
| **AWS Data Wrangler** | awswrangler | 3.14+ | Integração Pandas + AWS |
| **Armazenamento** | Amazon S3 | - | Data Lake (Raw + Refined) |
| **Orquestração** | AWS Lambda | Python 3.13 | Scraper + Trigger |
| **ETL** | AWS Glue | Python 3.9 | Transformação de dados |
| **Catálogo** | AWS Glue Data Catalog | - | Metadados das tabelas |
| **Análise** | Amazon Athena | - | Consultas SQL |
| **Agendamento** | Amazon EventBridge | - | Execução diária automática |
| **Registro de Contêiner** | Amazon ECR | - | Repositório de imagens Docker |

## 10. Monitoramento e Observabilidade

### 10.1. Logs Estruturados

```python
# Todos os componentes utilizam logging padrão Python
logger.info(f"Extraindo {len(symbols)} símbolos: {symbols}")
logger.debug(f"Partição {data_partition}: {len(df_partition)} registros")
logger.error(f"Erro na leitura do S3: {e}", exc_info=True)
```

**Destinos:**
- Lambda: CloudWatch Logs (`/aws/lambda/function-name`)
- Glue: CloudWatch Logs (`/aws-glue/jobs/output`)

### 10.2. Métricas do CloudWatch

**Automáticas:**
- Lambda: Invocações, Duração, Erros, Throttles
- Glue: JobRunTime, Successes, Failures
- S3: Bytes transferidos, Requisições

**Dashboards Recomendados:**
- Volume de dados processados por dia
- Tempo médio de execução do Glue Job
- Taxa de sucesso/falha do pipeline


## 11. Licença

Este projeto foi desenvolvido como parte de atividade acadêmica na FIAP (Pós-Tech Machine Learning Engineering).

## 12. Créditos

**Desenvolvido por:** Higor Menezes e Narcélio Filho
**Instituição:** FIAP - Pós-Tech Machine Learning Engineering  
**Ano:** 2026  

---

<p align="center">
  <i>💰 Pipeline Serverless | 🚀 Event-Driven | 📊 Analytics-Ready</i>
</p>
