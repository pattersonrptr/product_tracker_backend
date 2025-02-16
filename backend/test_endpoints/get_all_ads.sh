#!/bin/bash
set -e

echo "Listando todos os anúncios..."
curl -X 'GET' \
  'http://localhost:8000/ads/' \
  -H 'accept: application/json' | python -m json.tool
