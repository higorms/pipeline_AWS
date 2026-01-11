import sys
import logging
import pandas as pd
import awswrangler as wr
from datetime import datetime, timedelta
from awsglue.utils import getResolvedOptions

# --- CONFIGURAÇÃO DE LOGGING ---
# Configura o logger para escrever no CloudWatch Logs
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Evita duplicidade de logs se o handler já existir
if not logger.handlers:
    logger.addHandler(handler)

# --- 1. CONFIGURAÇÃO E ARGUMENTOS ---
try:
    # Tenta pegar o argumento da Lambda.
    args = getResolvedOptions(sys.argv, ['DATA_PROCESSAMENTO'])
    data_ref_str = args['DATA_PROCESSAMENTO']
except Exception as e:
    # Se falhar (teste local), usa data atual e emite um aviso.
    logger.warning("Argumento DATA_PROCESSAMENTO não encontrado. Usando data atual para referência.")
    data_ref_str = datetime.now().strftime("%Y-%m-%d")

# Converte string para datetime
try:
    data_ref = datetime.strptime(data_ref_str, "%Y-%m-%d")
except ValueError as e:
    logger.error(f"Formato de data inválido: {data_ref_str}. Esperado YYYY-MM-DD.")
    sys.exit(1)

# Configurações de Infraestrutura
bucket_name = "fiap-mlet-finance"
db_glue = "fiap_stocks_db"
tabela_glue = "stocks_resume"

logger.info("--- INÍCIO DO JOB ---")
logger.info(f"Data de referência solicitada: {data_ref_str}")

# --- 2. LEITURA DE ARQUIVOS (LÓGICA DOS 7 DIAS) ---
caminhos_leitura = []
# Gera pastas dos últimos 7 dias (D-6 até D) para o cálculo da janela móvel
for i in range(7):
    d = data_ref - timedelta(days=i)
    # Hive Style: raw/year=YYYY/month=MM/day=DD
    path = f"s3://{bucket_name}/raw/year={d.year}/month={d.month:02d}/day={d.day:02d}/"
    caminhos_leitura.append(path)

arquivos_para_ler = []
logger.info(f"Verificando arquivos nas pastas: {caminhos_leitura}")

# Lista arquivos manualmente para evitar erro de dataset=True com lista de caminhos
for prefix in caminhos_leitura:
    try:
        files = wr.s3.list_objects(path=prefix, suffix=".parquet")
        arquivos_para_ler.extend(files)
    except Exception as e:
        # Loga como aviso leve, pois é normal falhar em feriados
        logger.debug(f"Pasta não encontrada ou vazia (ignorado): {prefix}")
        continue

if not arquivos_para_ler:
    logger.warning("Nenhum arquivo .parquet encontrado nas pastas listadas.")
    # Encerra com sucesso (0) para não marcar erro no painel, mas avisa no log.
    sys.exit(0)

logger.info(f"Total de arquivos encontrados: {len(arquivos_para_ler)}")

try:
    # Lê os arquivos
    df = wr.s3.read_parquet(path=arquivos_para_ler, dataset=False)
except Exception as e:
    # exc_info=True imprime o rastreamento completo do erro no CloudWatch
    logger.critical(f"Erro fatal na leitura do S3: {e}", exc_info=True)
    sys.exit(1)

# --- 3. LIMPEZA E PREPARAÇÃO DE TIPOS ---

coluna_data_origem = "date"

# Verifica se a coluna existe antes de tentar processar
if coluna_data_origem not in df.columns:
    logger.error(f"Coluna '{coluna_data_origem}' não encontrada no DataFrame. Colunas: {df.columns}")
    sys.exit(1)

df['data_pregao'] = pd.to_datetime(df[coluna_data_origem].astype(str).str.strip()).dt.normalize()

logger.info(f"Amostra de datas encontradas (Normalizadas): {df['data_pregao'].unique()}")

# --- 4. TRANSFORMAÇÕES ---

# Renomear colunas
df = df.rename(columns={
    'close': 'preco_fechamento',
    'open': 'preco_abertura',
    'high': 'alta_preco',
    'low': 'baixa_preco',
    'volume': 'volume_negociado',
    'symbol': 'codigo_acao'
})

# Ordenação OBRIGATÓRIA para o cálculo da média móvel
df.sort_values(by=['codigo_acao', 'data_pregao'], inplace=True)

# Cálculo: Média Móvel de 7 dias
df['media_movel_7d'] = (
    df.groupby('codigo_acao')['preco_fechamento']
    .rolling(window=7, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

# Cálculo: Volume acumulado
df['volume_acumulado'] = df.groupby('codigo_acao')['volume_negociado'].cumsum()

# --- 5. FILTRAGEM INTELIGENTE ---

# Pega a data mais recente presente nos dados
data_maxima = df['data_pregao'].max()

logger.info(f"Data mais recente encontrada nos dados (MAX): {data_maxima}")

# Filtra mantendo apenas o dia mais novo
df_final = df[df['data_pregao'] == data_maxima].copy()

qtd_linhas = len(df_final)
logger.info(f"Linhas restantes após filtro: {qtd_linhas}")

if df_final.empty:
    logger.error("ERRO LÓGICO: O DataFrame ficou vazio após o filtro. Verifique se há dados correspondentes à data máxima.")
    sys.exit(1)

# --- 6. ESCRITA E CATALOGAÇÃO ---
logger.info(f"Salvando {qtd_linhas} linhas na camada refined...")

try:
    res = wr.s3.to_parquet(
        df=df_final,
        path=f"s3://{bucket_name}/refined/",
        dataset=True,
        mode="overwrite_partitions",
        partition_cols=["data_pregao", "codigo_acao"],
        database=db_glue,
        table=tabela_glue,
        compression="snappy"
    )
    logger.info(f"SUCESSO! Tabela {db_glue}.{tabela_glue} atualizada e dados persistidos.")
except Exception as e:
    logger.error(f"Erro na escrita/catalogação: {e}", exc_info=True)
    sys.exit(1)
