#!/bin/bash

#exec > >(tee ./log.txt) 2>&1

# Build the Docker image
#docker build -t dev_gpt . &&
# Run the Docker container, mounting the current directory
#docker run -it --rm -v "$(pwd):/app" --env OPENAI_API_KEY  dev_gpt
script -F log.txt poetry run python ./dev_gpt.py
