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
# the site restarts once while it installs itself, so wait until the administrator can log in twice in a row
ok=0
until [ "$ok" -ge 2 ]; do
  if curl -fs -X POST http://localhost:9080/answer/api/v1/user/login/email -H 'Content-Type: application/json' \
       -d '{"e_mail":"admin@acme.example","pass":"Adm1n-Pass-2024"}' 2>/dev/null | grep -q access_token; then ok=$((ok+1)); else ok=0; fi
  i=$((i+1)); [ "$i" -gt 120 ] && { echo "the site did not come up"; exit 1; }
  sleep 2
done
python3 "$here/seed.py" http://localhost:9080 admin@acme.example 'Adm1n-Pass-2024' "$dest/accounts.json"
echo "site: http://localhost:9080   accounts, tokens and API keys: $dest/accounts.json"
