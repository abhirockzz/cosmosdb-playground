import sys
import json
import argparse
import os
import uuid
from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Default Emulator Credentials - can be overridden via environment variable
ENDPOINT = os.getenv("COSMOS_ENDPOINT", "http://cosmosdb:8081")
KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="JSON data to seed (or path to file)")
    parser.add_argument("--query", help="SQL query text (or path to file)")
    args = parser.parse_args()

    # Create CosmosClient with connection settings that respect the provided endpoint
    # Set connection_verify=False for emulator SSL and enable_endpoint_discovery=False
    # to prevent the SDK from resolving endpoints
    client = CosmosClient(
        ENDPOINT,
        credential=KEY,
        connection_verify=False,
        enable_endpoint_discovery=False,
        preferred_locations=None,
    )

    db_name = "codapi_db"
    container_name = "codapi_container"

    # 1. Setup Database and Container
    # In a persistent container scenario, we might want to clean up previous runs or use unique IDs.
    # For simplicity, we'll recreate the container each time to ensure a clean state.
    try:
        db = client.create_database_if_not_exists(id=db_name)

        # Delete container if exists to clean up previous data
        try:
            db.delete_container(container_name)
        except exceptions.CosmosResourceNotFoundError:
            pass

        container = db.create_container(
            id=container_name, partition_key=PartitionKey(path="/id")
        )
    except Exception as e:
        print(f"Error connecting or setting up Cosmos DB: {e}")
        sys.exit(1)

    # 2. Seed Data
    if args.setup:
        try:
            # Check if it's a file path or direct JSON
            if os.path.exists(args.setup):
                with open(args.setup, "r") as f:
                    data = json.load(f)
            else:
                # Assume it's JSON string
                data = json.loads(args.setup)

            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = [data]
            else:
                items = []

            for item in items:
                # Ensure ID exists
                if "id" not in item:
                    item["id"] = str(uuid.uuid4())
                container.create_item(body=item)

        except Exception as e:
            print(f"Error seeding data: {e}", file=sys.stderr)
            sys.exit(1)

    # 3. Execute Query
    if args.query:
        try:
            # Check if it's a file path or direct SQL
            if os.path.exists(args.query):
                with open(args.query, "r") as f:
                    query_text = f.read()
            else:
                # Assume it's SQL string
                query_text = args.query

            # Execute Query
            items = list(
                container.query_items(
                    query=query_text, enable_cross_partition_query=True
                )
            )

            # Output Result as JSON
            print(json.dumps(items, indent=2))

        except exceptions.CosmosHttpResponseError as e:
            # Extract clean error message from Cosmos DB response
            import re

            error_str = str(e)
            # Try to extract just the message field using regex
            message_match = re.search(r'"message":\s*"([^"]+)"', error_str)

            if message_match:
                print(f"Error: {message_match.group(1)}", file=sys.stderr)
            else:
                # Fallback to status code if we can't extract message
                print(
                    f"Error executing query: Status code {e.status_code}",
                    file=sys.stderr,
                )

            sys.exit(1)
        except Exception as e:
            print(f"Error executing query: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
