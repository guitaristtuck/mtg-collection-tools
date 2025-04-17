#!/bin/bash

# Run poetry install
poetry install

PROJECT_NAME=$(tomlq -r '.project.name' pyproject.toml)

CACHE_DIR=/root/.cache/pypoetry/virtualenvs
CACHE_NAME=$(ls -d ${CACHE_DIR}/$(echo ${PROJECT_NAME}-* | tr _ -))

# move poetry to a deterministic file location
mv $CACHE_NAME ${CACHE_DIR}/${PROJECT_NAME}
ln -s ${CACHE_DIR}/${PROJECT_NAME} ${CACHE_NAME} 