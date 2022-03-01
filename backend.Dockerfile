FROM python:3.9

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc libffi-dev g++
WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=240 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.3

#RUN pip install "poetry==$POETRY_VERSION"
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN curl -sSL https://install.python-poetry.org | python -

# make sure poetry can be run
ENV PATH="$HOME/.local/bin:$PATH" 

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root

RUN mkdir deva
COPY deva ./deva
RUN poetry install 

COPY server/mlserver/app.py server/mlserver/util.py server/mlserver/run_prod.sh server/mlserver/gen_key.sh server/mlserver/prod.cfg ./

RUN poetry run ./gen_key.sh

CMD ["poetry", "run", "./run_prod.sh"]
