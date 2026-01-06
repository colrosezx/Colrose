#!/bin/sh
set -e

SECRET_FILE=/run/secrets/backend_env

if [ -f "$SECRET_FILE" ]; then
  echo "Loading environment variables from secret file..."
  while IFS= read -r line || [ -n "$line" ]; do
    # Strip carriage return and leading/trailing whitespace
    clean_line=$(echo "$line" | tr -d '\r' | sed 's/^[ \t]*//;s/[ \t]*$//')
    if [ -n "$clean_line" ] && ! echo "$clean_line" | grep -q '^\s*#'; then
      export "$clean_line"
    fi
  done < "$SECRET_FILE"
  echo "Environment variables loaded."
else
  echo "Secret file not found, continuing with existing environment variables."
fi

exec "$@"
