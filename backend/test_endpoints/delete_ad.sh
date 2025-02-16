#!/bin/bash
set -e

ID=$(grep -o '"id": [0-9]*' created_ad.json | cut -d' ' -f2)
echo "Deletando anúncio ID: $ID..."

curl -X 'DELETE' \
  "http://localhost:8000/ads/$ID" \
  -H 'accept: application/json'

echo -e "\nVerificando exclusão..."
curl -X 'GET' \
  "http://localhost:8000/ads/$ID" \
  -H 'accept: application/json' || true
