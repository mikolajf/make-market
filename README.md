# Make Market

This is a **learning project** designed to explore and understand the following concepts:

- Asynchronous and multithreaded programming
- Publish-subscribe mechanism leveraging IPC
- Kafka messaging
- Reliable Postgres update deliveries
- Usage of **ZeroMQ** for queue management
- **AvroSchema** for message serialization/deserialization
- **WebSocket** as a means of connecting to external systems (e.g., crypto exchanges)

## Project Overview

The goal of this project is to simulate a simplistic **market maker pricing system**. The system includes:

1. **Vendor-Specific Subscribers**: Components that subscribe to and process data from individual vendors.
2. **Aggregation Applications**: Applications that combine data from multiple exchanges to provide aggregated pricing information.
3. **Pub-Sub Infrastructure**: A publish-subscribe mechanism leveraging IPC as the communication medium to facilitate efficient data exchange between components.
4. **External Connectivity**: Integration with external systems using WebSocket, adhering to crypto exchange standards.

## Architecture

The project is structured using the **Pants build system** with a focus on modularity and scalability. The architecture is divided into:

- **Bases**: Foundational libraries and utilities.
- **Components**: Reusable modules that implement specific functionalities.
- **Projects**: Higher-level applications that integrate components to achieve specific goals.

## Learning Objectives

This project is intended to provide hands-on experience with:

- Designing and implementing concurrent systems.
- Leveraging Kafka for messaging and event-driven architectures.
- Ensuring data consistency and reliability in distributed systems.
- Structuring codebases for maintainability and scalability using Pants.
- Implementing queue management with ZeroMQ.
- Using AvroSchema for efficient message serialization and deserialization.
- Establishing WebSocket-based communication with external systems.

## Disclaimer

This project is for educational purposes only.
