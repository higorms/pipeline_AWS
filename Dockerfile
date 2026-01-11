FROM public.ecr.aws/lambda/python:3.13

# Define variáveis de ambiente para otimizar o Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Adiciona Poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copia arquivos de dependências
COPY pyproject.toml ./

# Instala dependências do projeto
RUN poetry install --no-root --no-dev

# Copia o código fonte
COPY src/ ${LAMBDA_TASK_ROOT}/

# Define o handler do Lambda
CMD ["main.lambda_handler"]
