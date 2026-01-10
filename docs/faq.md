# Azure Cosmos DB Playground - FAQs

Here are answers to some common questions about the Azure Cosmos DB Playground.

> Check out the features section in the [docs](features.md) to learn more.

## Is this connected to a real Azure Cosmos DB account?

No. This is an in-browser playground. It also has a backend component which uses the [Azure Cosmos DB vNext emulator](https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-linux). You don’t need an Azure subscription, account, or credentials to use it.

## What query language does the playground support?

The playground supports [Azure Cosmos DB SQL (Core API) queries](https://learn.microsoft.com/en-us/cosmos-db/query/). It’s designed to help you explore query syntax, patterns, and behavior using JSON data.

## Do queries modify or persist data anywhere?

No. All data exists only in your browser session. Queries run against the in-memory dataset you’re working with and do not affect any external systems.

## What happens when I refresh the page?

If you’ve modified the dataset or query, the playground will detect a saved session.
You’ll be prompted to **restore** your previous state or start fresh.

## What exactly is included in a shareable link?

A **shareable link** captures the dataset **and** query currently active in the playground. Opening the link restores that exact state so others can access, run, and modify the same example immediately.

## Is my data sent anywhere when I use the playground?

Yes and No. The playground **does** send the datasets or queries to the backend server component (for execution), but **does not** store them permanently.

## Can I use this for production workloads or benchmarking?

No. This is an experimental, exploratory tool. It’s meant for learning, prototyping, and explaining ideas — not for performance testing or production use.

## Can I embed this in my own site?

Yes. The playground is designed to be embedded in blogs, documentation, and tutorials.
This allows readers to interact with live data and queries directly alongside written explanations.

## What is this playground best suited for?

Depends on your imagination!

Here are some common use cases:

- Learning Cosmos DB SQL queries
- Exploring data models
- Creating runnable examples
- Teaching or explaining query behavior interactively