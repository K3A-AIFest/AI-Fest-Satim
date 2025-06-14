# Security Standards Tracker

This tool automates the tracking of security standards updates by:

1. Searching the web for security standards news
2. Comparing them with existing standards in the vector database
3. Storing new versions with detailed versioning information
4. Providing an API to access different versions of standards

![Security Standards Tracker Overview](https://via.placeholder.com/800x400?text=Security+Standards+Tracker+Overview)

## Features

- **Automated News Retrieval**: Searches for updates to major security standards like NIST, ISO 27001, PCI DSS, etc.
- **Versioning System**: Tracks different versions of the same standard over time
- **Change Detection**: Identifies and records changes between versions
- **REST API**: Provides endpoints to access standards and their versions
- **Vector Search**: Leverages existing vector database for semantic search

## Installation

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Additional dependencies specific to this tool
pip install fastapi uvicorn numpy
```

## Usage

### Fetching Security Standards Updates

Run the script in fetch mode to search for updates and add them to the database:

```bash
python scripts/security_standards_tracker.py --mode fetch
```

It's recommended to run this command on a regular schedule (e.g., daily using cron).

### Running the API Server

To start the API server:

```bash
python scripts/security_standards_tracker.py --mode serve
```

The server will start on `http://0.0.0.0:8000`.

### Scheduled Execution

Use the scheduled runner script to run the tracker on a regular basis with automatic retries:

```bash
# Run with default settings
./scripts/scheduled_standards_tracker.py

# Run with notifications and custom output log
./scripts/scheduled_standards_tracker.py --notify --output /path/to/logs/tracking_log.txt
```

#### Setting up a Cron Job

To run the tracker automatically every day at 3 AM:

```bash
# Edit crontab
crontab -e

# Add the following line
0 3 * * * /path/to/python3 /path/to/scripts/scheduled_standards_tracker.py >> /path/to/tracker_log.log 2>&1
```

### Using the API Client

The API client script provides a convenient way to interact with the API:

```bash
# List all standards
./scripts/standards_api_client.py list

# Get specific standard
./scripts/standards_api_client.py get std_123456

# Get versions of a standard
./scripts/standards_api_client.py versions std_123456

# Get specific version
./scripts/standards_api_client.py version v_123456

# Get changes for a version
./scripts/standards_api_client.py changes v_123456

# Search standards
./scripts/standards_api_client.py search "encryption requirements"
```

## API Endpoints

- `GET /standards`: List all standards
- `GET /standards/{standard_id}`: Get information about a specific standard
- `GET /standards/{standard_id}/versions`: Get all versions of a specific standard
- `GET /versions/{version_id}`: Get a specific version of a standard
- `GET /versions/{version_id}/changes`: Get changes between this version and the previous one
- `GET /search?query={query}`: Search standards by keyword

## Directory Structure

The script creates and uses the following directories:

- `./db/llamaindex_store_standards`: The existing vector database for standards
- `./db/standards_versions`: Stores different versions of standards
- `./db/standards_changes`: Tracks changes between versions

## Example Flow

1. **Daily Update**:
   - Script fetches news about security standards
   - New versions are added to the database
   - Changes are tracked between versions

2. **Accessing Versions**:
   - Use the API to list available standards
   - Browse versions of a particular standard
   - See what changed between versions

## Implementation Notes

This implementation:

- Uses the existing vector database structure
- Adds versioning through a separate storage system
- Integrates with your current web search functionality
- Preserves compatibility with existing code
