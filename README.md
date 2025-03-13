# ⚡ Lightning MCP

[![GitHub stars](https://img.shields.io/github/stars/LNAgents/lightning-mcp?style=flat-square)](https://github.com/LNAgents/lightning-mcp/stargazers)
[![GitHub license](https://img.shields.io/github/license/LNAgents/lightning-mcp?style=flat-square)](https://github.com/LNAgents/lightning-mcp/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/LNAgents/lightning-mcp?style=flat-square)](https://github.com/LNAgents/lightning-mcp/issues)
[![GitHub forks](https://img.shields.io/github/forks/LNAgents/lightning-mcp?style=flat-square)](https://github.com/LNAgents/lightning-mcp/network)

Lightning MCP is an open-source bridge between the Bitcoin Lightning Network and the Model Context Protocol (MCP). It enables AI agents and software systems to seamlessly send and receive Bitcoin payments through a standardized interface.

> **Note:** This project is currently in alpha stage, providing a foundation for developers to build Lightning-enabled AI applications.

## 🚀 Features

- **Lightning Network Integration** - Create and pay invoices, manage channels, and route transactions
- **MCP Interface** - Implement Model Context Protocol endpoints for AI agent integration
- **Security** - Industry-standard encryption (TLS) and authentication mechanisms
- **Multiple Backends** - Supports LND with planned Core Lightning and Eclair integration
- **Simple Deployment** - Docker support and comprehensive configuration options

## 📋 Table of Contents

- [Technical Overview](#-technical-overview)
- [Implementation Details](#-implementation-details)
- [Installation](#-installation)
- [Usage Examples](#-usage-examples)
- [License](#-license)

## 🔍 Technical Overview

### Lightning Integration

- Implements standard Lightning Network protocols (BOLT specs) for fast, off-chain Bitcoin payments
- Support for creating and paying invoices, managing channels, and routing transactions
- Compatible with popular node implementations and external services

### MCP Interface

- Exposes Lightning Network operations as MCP "tools" for agent discovery and usage
- Flexible interface options (REST or RPC) to accommodate various deployment scenarios
- Structured tool definitions with parameter validation

### Security & Performance 

- TLS encryption for all communications
- Authentication via macaroons, tokens, or API keys
- Optimized for low latency and near-instant settlement
- Balanced design for both simplicity and production readiness

### Deployment Options

- Self-hosted deployment (VPS, bare-metal)
- Containerized deployment with Docker/Kubernetes
- Optional integration with external services for simplified channel management

## 💻 Implementation Details

### Repository Structure

```
lightning-mcp/
├── lightning_mcp/               # Main package
│   ├── server/                  # MCP server implementation
│   │   └── mcp_server.py        # MCP server core
│   ├── lightning/               # Lightning Network integration
│   │   ├── lnd_client.py        # LND API client
│   │   └── clightning_client.py # c-lightning API client
│   └── utils/                   # Utility functions
├── examples/                    # Example usage scripts
├── tests/                       # Test suite
├── requirements.txt             # Python dependencies
├── setup.py                     # Package installation script
└── README.md                    # This file
```

### Available MCP Tools

The server exposes these Lightning Network operations:

| Tool | Description | Status |
|------|-------------|--------|
| **Create Invoice** | Generate a Lightning invoice with specified amount | ✅ |
| **Pay Invoice** | Pay a Lightning invoice | ✅ |
| **Check Payment Status** | Verify the status of a payment | ✅ |
| **Get Wallet Balance** | Retrieve the current wallet balance | ✅ |
| **Get Channel Balance** | Retrieve the current channel balance | ✅ |
| **List Channels** | List all active Lightning channels | ✅ |
| **Open Channel** | Open a new Lightning channel with a node | ✅ |
| **Close Channel** | Close an existing Lightning channel | ✅ |

### Lightning Network Backend Support

| Implementation | Status |
|----------------|--------|
| **LND** | ✅ Implemented |
| **Core Lightning** | 🚧 In Progress |
| **Eclair** | 📅 Planned |
| **External Services** | 📅 Planned |

## 🔧 Installation

### Prerequisites

- Python 3.10+
- Access to a Lightning Network node (LND initially)
- [uv](https://github.com/astral-sh/uv) - Modern Python package installer (recommended)
- [Optional] Docker for containerized deployment

### Quick Start

```bash
# Clone the repository
git clone https://github.com/LNAgents/lightning-mcp.git
cd lightning-mcp

# Create and activate a virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your Lightning node connection
cp config.example.json config.json
# Edit config.json with your node details

# Run the server
python -m lightning_mcp.server.mcp_server
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t lightning-mcp .

# Run the container
docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json lightning-mcp
```

### Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 🔌 Usage Examples

### Creating a Lightning Invoice

```python
from lightning_mcp.lightning import LndClient

# Initialize the client with your LND node configuration
client = LndClient(
    rpc_server="localhost:10009",
    macaroon_path="~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon",
    tls_cert_path="~/.lnd/tls.cert"
)

# Create an invoice for 1000 satoshis
invoice = client.create_invoice(amount=1000, memo="Test payment")
print(f"Payment request: {invoice['payment_request']}")
```

### Paying a Lightning Invoice

```python
# Pay an invoice
payment = client.pay_invoice(payment_request="lnbc...")
print(f"Payment sent! Hash: {payment['payment_hash']}")
```

### MCP Server Integration

```python
from lightning_mcp.server import McpServer

# Initialize and start the MCP server
server = McpServer(config_path="config.json")
server.start()
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ⚡ by <a href="https://github.com/LNAgents">LNAgents</a>
</p>