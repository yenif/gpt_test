# Use the official Python image with the latest tag
FROM python:3.11

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

# Set the working directory in the container
WORKDIR /app

# Run poetry install to install dependencies
COPY pyproject.toml poetry.lock /app/
COPY vendor /app/vendor
RUN poetry install

# Install Ruby and Rails dependencies
RUN apt-get update && apt-get install -y ruby-full
RUN gem install rails

# Copy the local project files to the container
COPY . /app

# Set the command to run the application interactively
CMD ["poetry", "run", "python", "dev_gpt.py"]
