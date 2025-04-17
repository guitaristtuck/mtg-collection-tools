# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.231.6/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version to use
ARG PYTHON_VERSION="3.12"
FROM python:${PYTHON_VERSION}-slim

# Install extra packages
RUN apt update \
    && apt install -y git yq

# Poetry
ARG POETRY_VERSION="none"
RUN pip3 install poetry==${POETRY_VERSION}

RUN mkdir -p /workspace/mtg-collection-tools
WORKDIR /workspace/mtg-collection-tools

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY .devcontainer/poetry_setup.sh /tmp/poetry_setup.sh

RUN /tmp/poetry_setup.sh
