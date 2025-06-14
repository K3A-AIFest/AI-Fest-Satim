# Policy Evaluation System

This system evaluates security policies against standards, identifies gaps, checks compliance, and suggests enhancements using a mixture of expert agents.

## Features

1. **Gap Identification**: Identifies missing elements in policies compared to standards.
2. **Compliance Checking**: Evaluates how well policies comply with standards.
3. **Policy Enhancement**: Suggests improvements for policies based on gaps and compliance checks.

## Architecture

The system follows a multi-agent architecture with expert agents specialized in different aspects of policy evaluation:

- **Gap Checker Agent**: Identifies missing elements in policies
- **Compliance Checker Agent**: Evaluates compliance with standards
- **Policy Enhancer Agent**: Suggests improvements based on gaps and compliance issues

All agents use a combination of:
- Vector database retrieval for policies and standards
- Web search for additional context
- Query rewriting for improved search results

## API Endpoints

The system exposes the following REST API endpoints:

- **POST /api/v1/identify-gaps**: Identifies gaps in a policy
- **POST /api/v1/check-compliance**: Checks compliance of a policy
- **POST /api/v1/enhance-policy**: Suggests enhancements for a policy
- **POST /api/v1/evaluate-policy**: Comprehensive evaluation (all three functions)

## Setup & Installation

### Prerequisites

- Python 3.8+
- pipenv or virtualenv
- Access to language models (Gemini API key)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd AI-Fest-Satim
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   ```

   Edit .env and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TAVI_API_KEY=your_tavily_api_key
   ```

### Running the Server

Start the FastAPI server:
```
python main.py
```

By default, the server runs on port 8000. You can change this by setting the PORT environment variable.

## Usage Example

### Identify Gaps in a Policy

```python
import requests
import json

url = "http://localhost:8000/api/v1/identify-gaps"
payload = {
    "policy": "Your policy text here...",
    "standards": ["Standard 1 text...", "Standard 2 text..."]
}

response = requests.post(url, json=payload)
results = response.json()

print(json.dumps(results, indent=2))
```

### Check Compliance

```python
url = "http://localhost:8000/api/v1/check-compliance"
payload = {
    "policy": "Your policy text here...",
    "standards": ["Standard 1 text...", "Standard 2 text..."]
}

response = requests.post(url, json=payload)
results = response.json()

print(json.dumps(results, indent=2))
```

### Enhance a Policy

```python
url = "http://localhost:8000/api/v1/enhance-policy"
payload = {
    "policy": "Your policy text here...",
    "standards": ["Standard 1 text...", "Standard 2 text..."]
}

response = requests.post(url, json=payload)
results = response.json()

print(json.dumps(results, indent=2))
```

## Response Format

The system returns JSON responses with a consistent structure:

```json
{
  "results": [
    {
      "chunk_content": "Policy chunk text",
      "classification": "GOOD|MISSING|NON_COMPLIANT",
      "gaps_identified": ["Gap 1", "Gap 2"],
      "justification": "Detailed explanation"
    },
    ...
  ]
}
```

## License

[Specify your license]
