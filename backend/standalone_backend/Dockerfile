FROM python:3.12-slim

LABEL maintainer="Julian Müller <julian2.mueller@tum.de>"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl

RUN curl -sSL 'https://install.python-poetry.org' | python -
#Add it to Path for the docker
ENV PATH="${PATH}:/root/.local/bin:/root/.poetry/bin"
#Add it to Path in case someone logs into an interactive shell
RUN echo 'export PATH="/root/.local/bin:$PATH"' >> ~/.bashrc


COPY flask_server.py pyproject.toml diagram.dbml init_sqlite_backend.py gunicorn.sh  /app/
COPY scripts /app/scripts
COPY resources /app/resources
RUN poetry install

RUN mkdir /app/data
RUN poetry run python -u init_sqlite_backend.py

# Expose Flask port
EXPOSE 3000


RUN chmod 775 /app/gunicorn.sh
ENTRYPOINT '/app/gunicorn.sh'
