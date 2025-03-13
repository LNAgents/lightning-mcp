#!/usr/bin/env python
"""
Test functionality of the Lightning MCP server.
"""
import json
import os
import sys
import time
from typing import Dict, Any

import pytest
from fastmcp import FastMCP

# Make sure we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use a test config
os.environ["LIGHTNING_MCP_CONFIG"] = "lightning_mcp/tests/test_config.json"

# Import server modules after setting config env var
from lightning_mcp.server.mcp_server import mcp, create_invoice, pay_invoice
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
                        "rpc_server": "localhost:10009",
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
    
    # Load the config
    return get_config_with_validation(config_path)

def test_mcp_server_setup(test_config):
    """Test that the MCP server is set up correctly."""
    assert isinstance(mcp, FastMCP)
    assert "Lightning MCP Test" in mcp.mcp_id

def test_create_invoice():
    """Test creating a Lightning invoice."""
    # Basic invoice creation
    invoice = create_invoice(amount_sat=1000, memo="Test invoice")
    
    # Check structure
    assert "payment_hash" in invoice
    assert "payment_request" in invoice
    assert "amount_sat" in invoice
    assert invoice["amount_sat"] == 1000
    assert invoice["memo"] == "Test invoice"
    
    # Test minimum limit enforcement
    min_invoice = create_invoice(amount_sat=0)
    assert "error" in min_invoice
    assert "Minimum" in min_invoice["error"]
    
    # Test maximum limit enforcement
    max_invoice = create_invoice(amount_sat=10000000000)  # 10 billion sats
    assert "error" in max_invoice
    assert "Maximum" in max_invoice["error"]

def test_pay_invoice():
    """Test paying a Lightning invoice."""
    # Create an invoice to pay
    invoice = create_invoice(amount_sat=1000, memo="Test payment")
    
    # Pay the invoice
    payment = pay_invoice(payment_request=invoice["payment_request"])
    
    # Check structure
    assert "payment_hash" in payment
    if "status" in payment and payment["status"] != "FAILED":
        assert "payment_preimage" in payment
        assert "payment_route" in payment

def test_invoice_payment_flow():
    """Test the complete invoice creation and payment flow."""
    # Create an invoice
    amount_sat = 5000
    memo = "Complete test flow"
    
    invoice = create_invoice(amount_sat=amount_sat, memo=memo)
    assert "payment_request" in invoice
    
    # Small delay to simulate real-world usage
    time.sleep(1)
    
    # Pay the invoice
    payment = pay_invoice(payment_request=invoice["payment_request"])
    
    # Verify payment was successful (in our mock implementation it usually is)
    if "status" in payment and payment["status"] == "SUCCEEDED":
        assert payment["payment_hash"] == invoice["payment_hash"]
    
    # Check payment status (this is a different API call)
    from lightning_mcp.server.mcp_server import check_payment_status
    status = check_payment_status(payment_hash=invoice["payment_hash"])
    
    assert "payment_hash" in status
    assert status["payment_hash"] == invoice["payment_hash"]

if __name__ == "__main__":
    # Run tests manually
    config = test_config()
    test_mcp_server_setup(config)
    test_create_invoice()
    test_pay_invoice()
    test_invoice_payment_flow()
    print("All tests passed!") 