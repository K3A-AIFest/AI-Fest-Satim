# Security Standards Tracker

A comprehensive system for tracking security standards updates, versioning them, and making them searchable through a vector database.

## Features

- **Automated News Retrieval**: Automatically searches the web for updates to major security standards like NIST, ISO 27001, PCI DSS, etc.
- **Versioning System**: Tracks different versions of the same standard over time to maintain a historical record
- **Change Detection**: Identifies and records changes between different versions of a standard
- **Vector Database Integration**: Seamlessly adds new standards to the existing vector database for semantic search
- **REST API**: Provides endpoints to access standards, their versions, and search functionality
- **Scheduled Updates**: Can be run on a schedule to keep standards up-to-date

## Directory Structure

```
security_standards_tracker/
├── __init__.py         # Package initialization
├── api_server.py       # FastAPI server entry point 
├── config.py           # Configuration settings
├── scheduled_tracker.py# Script for scheduled runs
├── tracker_cli.py      # Command-line interface
├── api/                # API-related modules
│   ├── __init__.py
│   └── routes.py       # API routes definition
├── core/               # Core functionality
│   ├── __init__.py
│   ├── tracker.py      # Main tracker functionality
│   ├── version_manager.py # Standards versioning
│   └── web_fetcher.py  # Web search functionality
├── models/             # Data models
│   ├── __init__.py
│   └── data_models.py  # Pydantic models
├── tests/              # Test modules
│   ├── __init__.py
│   └── test_integration.py # Integration tests
└── utils/              # Utility functions
    ├── __init__.py
    └── common.py       # Common utility functions
```

## Installation

1. Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

2. Additional dependencies specific to this tool:

```bash
pip install fastapi uvicorn numpy
```

## Usage

### Fetching Security Standards Updates

Run the tracker to search for updates and add them to the database:

```bash
python -m security_standards_tracker.tracker_cli
```

### Running the API Server

To start the API server:

```bash
python -m security_standards_tracker.api_server
```

The server will start on `http://0.0.0.0:8000`.

### Scheduled Execution

To set up a scheduled execution (e.g., via cron):

```bash
# Example crontab entry (runs daily at 3 AM)
0 3 * * * /path/to/python3 /path/to/security_standards_tracker/scheduled_tracker.py
```

## API Endpoints

- `GET /standards`: List all standards
- `GET /standards/{standard_id}`: Get information about a specific standard
- `GET /standards/{standard_id}/versions`: Get all versions of a specific standard
- `GET /versions/{version_id}`: Get a specific version of a standard
- `GET /versions/{version_id}/changes`: Get changes between this version and the previous one
- `GET /search?query={query}`: Search standards by keyword

## Storage

The system uses the following directories for storage:

- `./db/llamaindex_store_standards`: The existing vector database for standards
- `./db/standards_versions`: Stores different versions of standards
- `./db/standards_changes`: Tracks changes between versions

## Development

### Running Tests

```bash
python -m unittest discover -s security_standards_tracker/tests
```

### Test Coverage

To generate test coverage:

```bash
pip install coverage
coverage run -m unittest discover -s security_standards_tracker/tests
coverage report
```

## Design Principles

1. **DRY (Don't Repeat Yourself)**: Modular code with clear separation of concerns
2. **Single Responsibility**: Each module has a clear, focused purpose
3. **Extensibility**: Easy to add new features or modify existing ones
4. **Error Handling**: Comprehensive logging and error handling
5. **Testing**: Unit and integration tests to ensure functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.
