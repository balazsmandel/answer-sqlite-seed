#!/bin/sh
# Stands up the starting state: one Apache Answer 2.0.3 site on SQLite with existing content.
#   site -> ~/answer, http://localhost:9080   (admin@acme.example / see docker-compose.yml)
set -e
here="$(cd "$(dirname "$0")" && pwd)"
dest="$HOME/answer"
if [ -e "$dest" ]; then echo "$dest already exists, not touching it"; exit 1; fi
mkdir -p "$dest/data"
cp "$here/docker-compose.yml" "$dest/"
(cd "$dest" && docker compose up -d)
echo "waiting for the site..."
i=0
until curl -fs http://localhost:9080/answer/api/v1/siteinfo >/dev/null 2>&1; do
  i=$((i+1)); [ "$i" -gt 90 ] && { echo "the site did not come up"; exit 1; }
  sleep 2
done
python3 "$here/seed.py" http://localhost:9080 admin@acme.example 'Adm1n-Pass-2024' "$dest/accounts.json"
echo "site: http://localhost:9080   accounts, tokens and API keys: $dest/accounts.json"
