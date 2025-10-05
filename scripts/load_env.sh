#!/bin/bash
# Loads environment variables from .env file into the current shell session
# Usage: source ./scripts/load_env.sh

ENV_FILE="../.env"
if [ ! -f "$ENV_FILE" ]; then
  echo ".env file not found at $ENV_FILE"
  return 1
fi

while IFS='=' read -r name value; do
  # Skip comments and empty lines
  if [[ "$name" =~ ^# ]] || [[ -z "$name" ]]; then
    continue
  fi
  # Remove surrounding quotes from value
  value="${value%\"}"; value="${value#\"}"
  export "$name"="$value"
done < "$ENV_FILE"
echo "Loaded environment variables from $ENV_FILE"
