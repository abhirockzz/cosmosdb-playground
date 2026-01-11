# Limitations ⚠️

> Check the features section in the [docs](features.md) to learn more, or the FAQs section in the [docs](faq.md) for common questions.

While the playground is great for learning and experimentation, keep these limitations in mind. This is a sandbox environment meant for experimentation and learning, not for production use cases or sensitive data.
  
## Dataset Size

The playground is designed for small datasets suitable for demos and learning. It's not intended for testing with very large JSON files containing thousands of records or production-scale workloads.

## Performance

The playground is not optimized for performance. Query execution times may vary and are not indicative of real-world Cosmos DB performance.

## vNext Emulator Limitations

At the time of writing, the Azure Cosmos DB vNext emulator used in the playground *may not* support all features available in the full Azure Cosmos DB service. Refer to the [emulator documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-linux) for up to date information.

## Database and Containers

The playground currently supports one Cosmos DB container. You cannot create multiple containers or databases within the playground environment.

## Partition key selection

> May be not a limitation, but worth bearing in mind

The playground currently uses `/id` as the partition key for all queries and automatically generates a unique `id` for each item if it’s missing. In production Cosmos DB deployments, you should choose partition keys based on your specific access patterns and workload characteristics. Learn more about [partition key selection](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview).