# Pipeline de Dados B3 - Requisito 1 ✅

## 📋 Sobre o Projeto

Este é o **Requisito 1** do Tech Challenge: Pipeline Batch Bovespa para extração, processamento e análise de dados de ações e índices da B3.

### ✅ Requisito 1 Implementado

**Scrap de dados de ações ou índices da B3 com granularidade diária**

A implementação atual extrai dados da B3 usando a biblioteca `yfinance` e salva os dados no formato Parquet particionado por data no S3.

## 🏗️ Arquitetura do Projeto

O projeto segue os princípios da **Clean Architecture**:

```
src/
├── domain/                    # Camada de Domínio
│   ├── entities/             # Entidades de negócio
│   └── repositories/         # Interfaces (contratos)
│       ├── storage_repository.py
│       └── data_source_repository.py
│
├── application/              # Camada de Aplicação
│   └── use_cases/           # Casos de uso
│       ├── upload_parquet_to_s3.py
│       └── extract_b3_data.py
│
├── infrastructure/          # Camada de Infraestrutura
│   ├── data_sources/       # Implementações de extração
│   │   ├── yfinance_data_source.py
│   │   └── b3_data_source.py (placeholder)
│   └── storage/           # Implementações de armazenamento
│       └── s3_storage_repository.py
│
└── main.py                 # Ponto de entrada
```

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (Orquestrador)                    │
└───────────────┬─────────────────────────┬───────────────────────┘
                │                         │
                ▼                         ▼
    ┌───────────────────────┐ ┌────────────────────────────┐
    │ ExtractB3DataUseCase  │ │ UploadParquetToS3UseCase   │
    └───────────┬───────────┘ └──────────┬─────────────────┘
                │                        │
                ▼                        ▼
    ┌───────────────────────┐ ┌────────────────────────────┐
    │ YFinanceDataSource    │ │ S3StorageRepository        │
    │ (yfinance library)    │ │ (boto3)                    │
    └───────────────────────┘ └────────────────────────────┘
                │                        │
                ▼                        ▼
            [ B3 API ]              [ AWS S3 ]
```

## 🚀 Funcionalidades Implementadas

### 1. Extração de Dados (Requisito 1)
- ✅ Extração de múltiplas ações da B3
- ✅ Granularidade diária
- ✅ Suporte a índices (ex: ^BVSP - Ibovespa)
- ✅ Tratamento de erros por símbolo
- ✅ Uso da biblioteca `yfinance`

### 2. Armazenamento no S3
- ✅ Upload em formato Parquet
- ✅ Particionamento por data (`raw/date=YYYY-MM-DD/data.parquet`)
- ✅ Compressão automática
- ✅ Tratamento de erros de upload

### 3. Arquitetura Limpa
- ✅ Separação de responsabilidades
- ✅ Inversão de dependências
- ✅ Interfaces bem definidas
- ✅ Facilidade para testes

## 📦 Dependências

```toml
python = "^3.13"
python-dotenv = "^1.2.1"  # Variáveis de ambiente
boto3 = "^1.42.9"          # SDK AWS
pandas = "^2.0.0"          # Manipulação de dados
fastparquet = "^2024.11.0" # Formato Parquet
yfinance = "^0.2.0"        # Extração de dados B3
```

## ⚙️ Configuração

### 1. Instalar Dependências

```powershell
poetry install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
AWS_S3_BUCKET_NAME=seu-bucket-b3-data
AWS_REGION=us-east-1
```

### 3. Configurar Credenciais AWS

Você pode configurar as credenciais da AWS de duas formas:

**Opção A: AWS CLI (Recomendado)**
```powershell
aws configure
```

**Opção B: Variáveis de Ambiente**
Adicione ao arquivo `.env`:
```env
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
```

## 🎯 Como Executar

### Executar o Pipeline Completo

```powershell
poetry run python src/main.py
```

### Exemplo de Saída

```
======================================================================
  PIPELINE DE EXTRAÇÃO DE DADOS DA B3
======================================================================

📋 Configurações:
   Bucket S3: meu-bucket-b3-data
   Região: us-east-1
   Símbolos: 8
   Período: 2024-11-14 até 2024-12-14

======================================================================
  ETAPA 1: EXTRAÇÃO DE DADOS
======================================================================

📥 Iniciando extração de 8 símbolos...
   Período: 2024-11-14 até 2024-12-14

📊 Extraindo dados de ^BVSP...
   ✓ 21 registros extraídos
📊 Extraindo dados de PETR4.SA...
   ✓ 21 registros extraídos
📊 Extraindo dados de VALE3.SA...
   ✓ 21 registros extraídos

✓ Extraídos 168 registros no total
   Datas únicas: 21
   Símbolos únicos: 8

======================================================================
  ETAPA 2: PARTICIONAMENTO E UPLOAD
======================================================================

📦 Particionando dados em 21 datas...

📤 Enviando partição 2024-11-14...
   Registros: 8
   Destino: s3://meu-bucket-b3-data/raw/date=2024-11-14/data.parquet
   ✓ Sucesso!

...

======================================================================
  RESUMO DA EXECUÇÃO
======================================================================

✓ Total de registros extraídos: 168
✓ Partições criadas: 21
✓ Uploads bem-sucedidos: 21

✓ Pipeline executado com sucesso!
```

## 📊 Estrutura dos Dados Extraídos

Os dados são salvos com as seguintes colunas:

| Coluna  | Tipo     | Descrição                    |
|---------|----------|------------------------------|
| date    | date     | Data do pregão               |
| symbol  | string   | Código do ativo (ex: PETR4.SA) |
| open    | float    | Preço de abertura            |
| high    | float    | Preço máximo                 |
| low     | float    | Preço mínimo                 |
| close   | float    | Preço de fechamento          |
| volume  | integer  | Volume negociado             |

## 📂 Estrutura no S3

```
s3://seu-bucket-b3-data/
└── raw/
    ├── date=2024-12-01/
    │   └── data.parquet
    ├── date=2024-12-02/
    │   └── data.parquet
    └── date=2024-12-03/
        └── data.parquet
```

## 🔄 Próximos Passos

### Requisitos Futuros do Tech Challenge

- [ ] **Requisito 2**: Trigger S3 → Lambda
- [ ] **Requisito 3**: Lambda → AWS Glue Job
- [ ] **Requisito 4**: Implementar Lambda
- [ ] **Requisito 5**: Job Glue com transformações
- [ ] **Requisito 6**: Salvar dados refinados
- [ ] **Requisito 7**: Catalogar no Glue Catalog
- [ ] **Requisito 8**: Consultas via Athena

## 🧪 Testes

Para testar a extração sem upload no S3, você pode modificar o `main.py` temporariamente ou criar um script de teste separado.

## 📝 Notas Técnicas

### Códigos de Ações da B3

Para usar a biblioteca `yfinance` com ações da B3, adicione `.SA` ao final do código:

- **PETR4** → `PETR4.SA` (Petrobras PN)
- **VALE3** → `VALE3.SA` (Vale ON)
- **IBOVESPA** → `^BVSP` (Índice Bovespa)

### Alternativa: Web Scraping

A classe `B3DataSource` está preparada como placeholder para implementação futura de scraping direto do site da B3 ou outros portais financeiros.

## 🤝 Contribuidores

- **Higor Menezes** - menezes.higor.98@gmail.com

## 📄 Licença

Este projeto faz parte do Tech Challenge da FIAP - Machine Learning Engineering.
