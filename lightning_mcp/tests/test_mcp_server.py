#!/usr/bin/env python
"""
Test functionality of the Lightning MCP server.
"""
import json
import os
import sys
import asyncio
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient
from fastmcp.tools.base import Tool
from fastmcp.utilities.types import ImageContent as TextContent

# Make sure we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import server modules
from lightning_mcp.server.mcp_server import LightningMCPServer
from lightning_mcp.utils.config import get_config_with_validation

@pytest.fixture
def test_config():
    """Create a test configuration."""
    # Check if test config exists, if not, create it
    config_path = "lightning_mcp/tests/test_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if not os.path.exists(config_path):
        # Create a minimal test config
        test_config = {
            "server": {
                "host": "localhost",
                "port": 8080,
                "debug": True,
                "log_level": "debug",
                "mcp_name": "Lightning MCP Test",
                "mcp_version": "0.1.0"
            },
            "security": {
                "tls_cert_path": "/path/to/tls.cert",
                "tls_key_path": "/path/to/tls.key",
                "token_auth_enabled": False,
                "api_tokens": []
            },
            "lightning": {
                "implementation": "lnd",
                "connection": {
                    "lnd": {
                        "host": "localhost",
                        "port": 10009,
                        "tls_cert_path": "~/.lnd/tls.cert",
                        "macaroon_path": "~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon",
                        "network": "mainnet"
                    }
                }
            },
            "payment_limits": {
                "min_payment_sat": 1,
                "max_payment_sat": 1000000,
                "daily_outbound_limit_sat": 5000000
            },
            "advanced": {
                "connection_timeout_seconds": 30,
                "payment_timeout_seconds": 60,
                "max_routing_fee_percent": 3
            }
        }
        
        with open(config_path, "w") as f:
            json.dump(test_config, f, indent=2)
    
    # Load and validate the config
    return get_config_with_validation(config_path)

@pytest.fixture
def mcp_server(test_config):
    """Create a test MCP server instance."""
    # Override config path for testing
    os.environ["CONFIG_PATH"] = "lightning_mcp/tests/test_config.json"
    
    # Create server instance
    server = LightningMCPServer()
    
    # Create FastAPI test client
    app = server.create_app()
    client = TestClient(app)
    
    return server, client

def test_server_initialization(mcp_server):
    """Test that the MCP server is initialized correctly."""
    server, client = mcp_server
    
    # Check server configuration
    assert server.config["server"]["mcp_name"] == "Lightning MCP Test"
    assert server.config["server"]["mcp_version"] == "0.1.0"
    
    # Check tool registration
    tools = asyncio.run(server.mcp_server.list_tools())
    assert len(tools) == 4
    assert any(t.name == "create_invoice" for t in tools)
    assert any(t.name == "pay_invoice" for t in tools)
    assert any(t.name == "check_payment" for t in tools)
    assert any(t.name == "get_wallet_balance" for t in tools)

def test_health_endpoint(mcp_server):
    """Test the health check endpoint."""
    server, client = mcp_server
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "node_info" in data
    assert data["node_info"]["implementation"] == "lnd"
    assert data["node_info"]["version"] == "0.1.0"

@pytest.mark.asyncio
async def test_create_invoice(mcp_server):
    """Test creating an invoice."""
    server, _ = mcp_server
    
    # Test valid invoice creation
    result = await server.handle_tool_call("create_invoice", {
        "amount": 1000,
        "memo": "Test payment"
    })
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    
    invoice_data = json.loads(result[0].text)
    assert "payment_request" in invoice_data
    assert invoice_data["payment_request"].startswith("ln")

@pytest.mark.asyncio
async def test_pay_invoice(mcp_server):
    """Test paying an invoice."""
    server, _ = mcp_server
    
    # Create an invoice first
    invoice_result = await server.handle_tool_call("create_invoice", {
        "amount": 1000,
        "memo": "Test payment"
    })
    invoice_data = json.loads(invoice_result[0].text)
    
    # Test paying the invoice
    result = await server.handle_tool_call("pay_invoice", {
        "payment_request": invoice_data["payment_request"]
    })
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    
    payment_data = json.loads(result[0].text)
    assert "payment_hash" in payment_data

@pytest.mark.asyncio
async def test_check_payment(mcp_server):
    """Test checking payment status."""
    server, _ = mcp_server
    
    # Create and pay an invoice first
    invoice_result = await server.handle_tool_call("create_invoice", {
        "amount": 1000,
        "memo": "Test payment"
    })
    invoice_data = json.loads(invoice_result[0].text)
    
    payment_result = await server.handle_tool_call("pay_invoice", {
        "payment_request": invoice_data["payment_request"]
    })
    payment_data = json.loads(payment_result[0].text)
    
    # Test checking the payment
    result = await server.handle_tool_call("check_payment", {
        "payment_hash": payment_data["payment_hash"]
    })
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    
    status_data = json.loads(result[0].text)
    assert "status" in status_data

@pytest.mark.asyncio
async def test_get_wallet_balance(mcp_server):
    """Test getting wallet balance."""
    server, _ = mcp_server
    
    result = await server.handle_tool_call("get_wallet_balance", {})
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    
    balance_data = json.loads(result[0].text)
    assert "total_balance" in balance_data
    assert "confirmed_balance" in balance_data
    assert "unconfirmed_balance" in balance_data

if __name__ == "__main__":
    pytest.main([__file__]) 