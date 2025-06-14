# API Testing Guide

This guide explains how to run and test the Policy Evaluation API endpoints.

## Prerequisites

1. Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
pip install -r scripts/test_requirements.txt
```

## Starting the API Server

1. To start the FastAPI server, run the following command from the project root:

```bash
python main.py
```

2. The server should start on port 8000 by default (http://localhost:8000).

3. You can access the API documentation at http://localhost:8000/docs

## Testing the API Endpoints

1. To run the test suite against the API endpoints, use:

```bash
python scripts/test_api.py
```

This will:
- Test the health check endpoint
- Test the gap identification endpoint
- Test the compliance check endpoint
- Test the policy enhancement endpoint
- Test the comprehensive evaluation endpoint
- (If python-docx is installed) Test with a real policy document

## API Endpoints

The API provides the following endpoints:

1. **Health Check**: 
   - GET `/health`
   - Verifies the API is operational

2. **Gap Identification**:
   - POST `/api/v1/identify-gaps`
   - Identifies gaps in a policy compared to standards

3. **Compliance Check**:
   - POST `/api/v1/check-compliance` 
   - Checks compliance of a policy against standards

4. **Policy Enhancement**:
   - POST `/api/v1/enhance-policy`
   - Suggests improvements for a policy to better align with standards

5. **Comprehensive Evaluation**:
   - POST `/api/v1/evaluate-policy`
   - Performs all three analyses in one call

## Making Manual API Requests

You can also test the API using curl or Postman:

```bash
curl -X POST "http://localhost:8000/api/v1/evaluate-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "Your policy text goes here...",
    "standards": ["Standard 1 text...", "Standard 2 text..."]
  }' | jq
```

## Testing with Real Data

The test script includes functionality to test with real policy documents from the `policies` folder. It will automatically:

1. Load a document (Information-Security-Policy.docx by default)
2. Send it to the API for evaluation
3. Save the results to a JSON file
