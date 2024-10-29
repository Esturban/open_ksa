# Stage 1: Build stage
FROM python:3.12.1-alpine AS build
RUN apk add --no-cache git build-base
WORKDIR /workspaces
# Copy the requirements.txt file and install dependencies
COPY requirements.txt /workspaces/
COPY examples/ open_ksa/ pyproject.toml .devcontainer/ .github/ /workspaces/

# Stage 2: Final stage
FROM python:3.12.1-alpine
RUN apk add --no-cache git
WORKDIR /workspaces
COPY --from=build /workspaces /workspaces
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt