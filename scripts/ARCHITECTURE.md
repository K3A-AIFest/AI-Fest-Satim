# Security Standards Tracker System Overview

## Architecture

The Security Standards Tracker is designed with the following components:

1. **Web Fetcher**: Periodically searches for updates to security standards using various search strategies.
2. **Version Manager**: Manages different versions of security standards with metadata and change tracking.
3. **Vector Database Integration**: Stores semantic representations of standards for similarity comparison and searching.
4. **REST API**: Provides endpoints to access and query the data.

## Data Flow

```
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                 │     │                   │     │                   │
│   Web Sources   │────▶│  Standards Tracker │────▶│  Version Manager  │
│                 │     │                   │     │                   │
└─────────────────┘     └───────────────────┘     └─────────┬─────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                 │     │                   │     │                   │
│      Client     │◀────│     REST API      │◀────│   Vector Database │
│   Applications  │     │                   │     │                   │
└─────────────────┘     └───────────────────┘     └───────────────────┘
```

## Components in Detail

### Web Fetcher
- Uses the Tavily Search API (via the existing `web.py` tool)
- Targets specific security standards sources (NIST, ISO, PCI DSS, etc.)
- Performs general searches for recent security standard updates

### Version Manager
- Stores different versions of the same standard
- Records metadata about each version (date, source, etc.)
- Tracks changes between versions
- Uses embedding similarity to identify when a new document is a version of an existing standard

### Vector Database Integration
- Utilizes the existing LlamaIndex-based vector database
- Stores embeddings for efficient semantic search
- Maintains document metadata including version information
- Allows searching across all versions or only the latest versions

### REST API
- Built with FastAPI for performance and automatic OpenAPI documentation
- Provides endpoints for browsing standards and versions
- Enables searching across standards
- Returns change information between versions

## Storage Structure

```
db/
├── llamaindex_store_standards/  # Main vector database
│   ├── default__vector_store.json
│   ├── docstore.json
│   └── ...
├── standards_versions/         # Versions storage
│   ├── standards_index.json    # Index of all standards and versions
│   ├── v_123456.json          # Version 1 of a standard
│   ├── v_789012.json          # Version 2 of the same standard
│   └── ...
└── standards_changes/         # Changes between versions
    ├── chg_123456.json        # Changes from version 1 to 2
    └── ...
```
