# Architecture Overview

This document provides an overview of the Azure Cosmos DB Playground architecture, including component interactions, and execution flow.

## System Architecture

Here is a simplified architecture of the Azure Cosmos DB Playground:

```
+-------------------+        +-------------------+        +-------------------+
|   User Browser    |  <---> |      nginx        |  <---> |     Codapi        |
| (playground.html) |        | (Reverse Proxy)   |        | (Sandbox Server)  |
+-------------------+        +-------------------+        +-------------------+
                                                           |
                                                           v
                                                +--------------------------+
                                                |  Ephemeral Query Container|
                                                |  (Python + Cosmos SDK)    |
                                                +--------------------------+
                                                           |
                                                           v
                                                +--------------------------+
                                                | Cosmos DB Emulator       |
                                                | (Docker Container)       |
                                                +--------------------------+
```

## Core Components

### Azure Cosmos DB vNext Emulator

The emulator is a **local** version of Azure Cosmos DB (SQL API) available as a Docker container. It *emulates* the real Azure Cosmos DB service, allowing users to experiment with queries and data models without any cloud setup or cost:

- Runs as a long-lived Docker container
- Provides SQL API endpoint at `http://cosmosdb:8081`

### Codapi

Codapi is a lightweight sandbox server designed for interactive documentation, code examples, and learning environments. In the playground, Codapi manages the creation of isolated Docker containers for each query execution.

**Key responsibilities:**

- Spawns ephemeral Docker containers for query execution
- Manages sandbox lifecycle and cleanup
- Enforces execution timeouts (15 seconds)
- Provides API for code execution from frontend

**Integration components:**

- **Codapi JavaScript widget** ([codapi-js](https://github.com/nalgeon/codapi-js)): Frontend integration that provides the interactive UI for code execution
- **Codapi API**: RESTful API for submitting code and receiving execution results

### nginx (Reverse Proxy)

nginx serves dual roles in the architecture:

1. **Static file server**: Serves frontend HTML files (`playground.html`, `run.html`) and dataset JSON files
2. **API proxy**: Routes API requests from browser to Codapi server

**Request routing:**

- Static content: `/*` → Served directly from nginx
- API requests: `/v1/*` → Proxied to Codapi server on port 1313

This configuration enables the frontend to make API calls without CORS issues and provides a single entry point for all playground functionality.

### Python Query Engine

The query engine (`sandboxes/cosmosdb/query.py`) is the execution runtime that runs inside ephemeral containers spawned by Codapi.

- Called via `wrapper.sh` which reads files from Codapi workspace
- Uses Azure Cosmos DB Python SDK for all database operations

### Frontend (Browser)

The frontend uses vanilla HTML/JavaScript with minimal dependencies:

- Codapi widget for interactive execution
- Plain JavaScript for UI interactions and state management
- Tailwind CSS for styling

## Query Execution Flow

The complete flow from user interaction to result display:

1. **User initiates query**: User clicks "Run" in the browser
2. **Frontend request**: Codapi widget sends POST request to nginx `/v1/exec` endpoint with:
   - Setup data (JSON array)
   - Query code (SQL string)
   - Sandbox name ("cosmosdb")
3. **nginx proxying**: nginx forwards request to Codapi server at `http://codapi:1313`
4. **Container spawning**: Codapi creates ephemeral Docker container from `codapi/cosmosdb-client` image
5. **Code execution**: Inside container:
   - `wrapper.sh` reads setup data and query from workspace files
   - Invokes `query.py --setup <data> --query <sql>`
   - Python connects to emulator at `http://cosmosdb:8081`
   - Creates temporary container with unique name
   - Seeds data from setup parameter
   - Executes SQL query
   - Captures results
   - Deletes temporary container
6. **Result return**: Codapi captures container stdout/stderr and returns to nginx
7. **Frontend display**: Browser receives response and displays results or errors

**Cleanup:**

- Ephemeral query container: Removed by Codapi after execution
- Temporary Cosmos DB container: Deleted by Python script after query completion
- No persistent data remains between executions

## References

- [Azure Cosmos DB Emulator](https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-linux)
- [Codapi Documentation](https://github.com/nalgeon/codapi) and [Custom Sandbox Guide](https://github.com/nalgeon/codapi/blob/main/docs/add-sandbox.md)
