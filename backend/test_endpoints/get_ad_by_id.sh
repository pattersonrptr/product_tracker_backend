#!/bin/bash
set -e

ID=$(grep -o '"id": [0-9]*' created_ad.json | cut -d' ' -f2)
echo "Buscando anúncio ID: $ID..."

curl -X 'GET' \
  "http://localhost:8000/ads/$ID" \
  -H 'accept: application/json' | python -m json.tool
