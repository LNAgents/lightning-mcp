# Lightning MCP

Lightning MCP is an open-source server bridging the Bitcoin Lightning Network with the Model Context Protocol (MCP). It allows automated agents (or other software) to send and receive Bitcoin payments over Lightning by exposing a standardized interface. This repository aims to deliver a **minimum viable product (MVP)** that’s easy to set up and extend.

---

## Technical High-Level Summary

1. **Lightning Integration**  
   - Uses standard Lightning protocols (BOLT specs) for off-chain Bitcoin payments.  
   - Supports creating and paying invoices, managing channels, and routing transactions.  
   - Compatible with popular node implementations (LND, Core Lightning, etc.) or external custodial services.

2. **MCP Interface**  
   - Implements Model Context Protocol endpoints so automated systems can discover and invoke “Lightning payment” functions directly.  
   - Designed to operate with either REST or RPC (JSON-RPC/gRPC) to suit varied deployment environments.

3. **Security & Performance**  
   - Adopts industry-standard encryption (TLS) and authentication (macaroons, tokens, or API keys).  
   - Targets low latency for near-instant payment settlement.  
   - Balances straightforward MVP design with readiness for production-scale throughput.

4. **Deployment**  
   - Can run self-hosted (e.g., on a VPS or bare-metal) or in the cloud (Docker/Kubernetes).  
   - Optional external services for simplified channel management and liquidity (e.g., LNPay, LNBits, Voltage).  
   - Provides basic configuration files to connect with a local Bitcoin node or a remote service.

---

## MVP Requirements

1. **Core Payment Flow**  
   - Ability to create and pay Lightning invoices.  
   - Basic channel operations (open, close, list channels).  
   - Simple REST or RPC interface (decide at build-time).

2. **Security**  
   - HTTPS/TLS for all incoming requests.  
   - Basic token-based auth or macaroons to control payment capabilities.  
   - Safe handling of private keys (file-based or encrypted storage).

3. **Integration**  
   - Model Context Protocol compliance (provide a schema or simple endpoint describing the Lightning “tool”).  
   - Optional plugin for a chosen Lightning node back end (LND by default).  
   - Minimal testing harness or example scripts to verify send/receive flow.

4. **Deployment & Documentation**  
   - Dockerfile and/or minimal instructions for local install.  
   - Configuration examples for common setups (e.g., pointing to an LND node).  
   - Clear README on how to run the server and test payments.

---

## Roadmap

1. **Phase 1: MVP**  
   - Implement invoice creation and payment features.  
   - Provide a single reference backend (e.g., LND).  
   - Add documentation for quick start and environment setup.  

2. **Phase 2: Extended Node Support**  
   - Integrate other Lightning back ends (Core Lightning, Eclair).  
   - Support more advanced channel features (e.g., multi-path payments, splicing).  

3. **Phase 3: Security & Robustness**  
   - Add rate-limiting, watchtower integration, and improved key management.  
   - Test for higher loads (up to hundreds or thousands of payments/second).  

4. **Phase 4: Advanced MCP Features**  
   - Richer schema definitions for AI agent discovery.  
   - Automatic payment event callbacks/notifications to AI clients (webhooks, SSE).  

5. **Phase 5: Community Extensions**  
   - Integration with LNURL, Lightning Addresses, or other user-friendly protocols.  
   - Larger ecosystem tools (monitoring dashboards, plugin frameworks).

---

## Getting Started

1. **Clone the Repo**  
   ```bash
   git clone https://github.com/LNAgents/lightning-mcp.git
   cd lightning-mcp