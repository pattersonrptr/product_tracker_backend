#!/bin/bash
set -e

echo "Criando novo anúncio..."
curl -X 'POST' \
  'http://localhost:8000/ads/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://exemplo.com/script1",
  "title": "Anúncio de Teste 1",
  "price": 299.90
}' | python -m json.tool > created_ad.json

echo -e "\nAnúncio criado com sucesso! Resposta salva em created_ad.json"
