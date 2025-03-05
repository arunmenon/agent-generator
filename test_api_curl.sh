#!/bin/bash

echo "Testing API endpoints on localhost:8000"

echo -e "\nTesting basic test endpoint:"
curl -v http://localhost:8000/test

echo -e "\n\nTesting flow create endpoint:"
curl -v -X POST "http://localhost:8000/flow/create" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Test task",
    "domain": "Test domain"
  }'

echo -e "\n\nDone with tests"