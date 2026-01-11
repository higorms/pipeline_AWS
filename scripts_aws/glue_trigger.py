import json
import boto3
import urllib.parse
import logging
import re
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    glue_client = boto3.client('glue')

    glue_job_name = os.environ.get('GLUE_JOB_NAME', 'stocks_resume')

    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')

        logger.info(f"Evento recebido. Bucket: {bucket}, Key: {key}")

        match = re.search(r'year=(\d+)/month=(\d+)/day=(\d+)', key)

        if match:
            year, month, day = match.groups()
            data_processamento = f"{year}-{month}-{day}"

            logger.info(f"Data extraída: {data_processamento}")

            response = glue_client.start_job_run(
                JobName=glue_job_name,
                Arguments={
                    '--DATA_PROCESSAMENTO': data_processamento
                }
            )

            return {
                'statusCode': 200,
                'body': json.dumps(f"Job iniciado: {response['JobRunId']}")
            }
        else:
            logger.error(f"Padrão de data não encontrado em: {key}")
            return {'statusCode': 400, 'body': "Data invalida"}

    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise e
