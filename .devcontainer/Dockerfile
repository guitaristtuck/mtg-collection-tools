# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.231.6/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version to use
ARG PYTHON_VERSION="3.12"
FROM --platform=linux/amd64 python:${PYTHON_VERSION}-slim

# Install extra packages
RUN apt update \
    && apt install -y git yq \
    && apt install -y libgl1-mesa-glx libegl1-mesa libfontconfig1 libglib2.0-0 libxkbcommon0 libdbus-1-3 \
    && apt install -y libwayland-dev libwayland-client0 libwayland-server0 \
    && apt install -y libxcb1 libxcb-cursor0 libxcb-render0 libxcb-shape0 libxcb-xfixes0 \
    && apt install -y qt6-base-dev qt6-qpa-plugins



# Poetry
ARG POETRY_VERSION="none"
RUN pip3 install poetry==${POETRY_VERSION}

RUN mkdir -p /workspace/mtg-collection-tools
WORKDIR /workspace/mtg-collection-tools

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY .devcontainer/poetry_setup.sh /tmp/poetry_setup.sh

RUN /tmp/poetry_setup.sh
