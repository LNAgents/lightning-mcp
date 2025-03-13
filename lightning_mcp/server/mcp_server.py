#!/usr/bin/env python
"""
Lightning MCP Server - Exposes Lightning Network functionality as MCP tools.
Simplified implementation for FastMCP 0.4.1 compatibility.
"""
import json
import os
import sys
from typing import Dict, List, Optional, Any

from fastmcp import FastMCP
from fastmcp.server import Context

# Import Lightning Network client implementations
from lightning_mcp.lightning.lnd_client import LNDClient
from lightning_mcp.lightning.clightning_client import CLightningClient

# Global variables
_ln_client = None
_config = None

# Helper function to load configuration
def load_config():
    config_path = os.environ.get("CONFIG_PATH", "config.json")
    with open(config_path) as f:
        return json.load(f)

# Helper function to get the Lightning client
def get_ln_client():
    global _ln_client, _config
    
    if _ln_client is not None:
        return _ln_client
    
    if _config is None:
        _config = load_config()
    
    try:
        implementation = _config["lightning"]["implementation"]
        print(f"Initializing {implementation} client...")
        
        if implementation == "lnd":
            _ln_client = LNDClient(_config["lightning"]["connection"]["lnd"])
        elif implementation == "c-lightning":
            conn_config = _config["lightning"]["connection"]["c-lightning"]
            print(f"Connecting to c-lightning at socket path: {conn_config['socket_path']}")
            _ln_client = CLightningClient(conn_config)
        else:
            print(f"Unsupported Lightning implementation: {implementation}")
            return None
        
        print(f"Successfully initialized {implementation} client")
        return _ln_client
    except Exception as e:
        print(f"Error initializing Lightning client: {e}")
        return None

# Initialize the FastMCP server
def init_server():
    # Load configuration for server settings
    config = load_config()
    
    # Extract server settings
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8080)
    debug = config.get("server", {}).get("debug", False)
    log_level = config.get("server", {}).get("log_level", "INFO").upper()
    
    # Create server instance
    server = FastMCP(
        name=config.get("server", {}).get("mcp_name", "Lightning MCP"),
        host=host,
        port=port,
        debug=debug,
        log_level=log_level
    )
    
    # Register tools
    @server.tool("lightning/createInvoice")
    def create_invoice(amount: int, memo: str = "", ctx: Context = None) -> Dict:
        """Create a Lightning Network invoice."""
        if ctx:
            ctx.info(f"Creating invoice for {amount} sats with memo: {memo}")
        
        try:
            ln_client = get_ln_client()
            if ln_client is None:
                return {"error": "Lightning client not available", "status": "error"}
                
            invoice = ln_client.create_invoice(amount, memo)
            return invoice
        except Exception as e:
            error_msg = f"Error creating invoice: {str(e)}"
            if ctx:
                ctx.error(error_msg)
            return {"error": error_msg, "status": "error"}
    
    @server.tool("lightning/payInvoice")
    def pay_invoice(payment_request: str, ctx: Context = None) -> Dict:
        """Pay a Lightning Network invoice."""
        if ctx:
            ctx.info(f"Paying invoice: {payment_request[:30]}...")
        
        try:
            ln_client = get_ln_client()
            if ln_client is None:
                return {"error": "Lightning client not available", "status": "error"}
                
            payment = ln_client.pay_invoice(payment_request)
            return payment
        except Exception as e:
            error_msg = f"Error paying invoice: {str(e)}"
            if ctx:
                ctx.error(error_msg)
            return {"error": error_msg, "status": "error"}
    
    @server.tool("lightning/checkPayment")
    def check_payment(payment_hash: str, ctx: Context = None) -> Dict:
        """Check the status of a Lightning Network payment."""
        if ctx:
            ctx.info(f"Checking payment status for hash: {payment_hash}")
        
        try:
            ln_client = get_ln_client()
            if ln_client is None:
                return {"error": "Lightning client not available", "status": "error"}
                
            payment_status = ln_client.check_payment(payment_hash)
            return payment_status
        except Exception as e:
            error_msg = f"Error checking payment: {str(e)}"
            if ctx:
                ctx.error(error_msg)
            return {"error": error_msg, "status": "error"}
    
    @server.tool("lightning/getWalletBalance")
    def get_wallet_balance(ctx: Context = None) -> Dict:
        """Get the current wallet balance."""
        if ctx:
            ctx.info("Retrieving wallet balance")
        
        try:
            ln_client = get_ln_client()
            if ln_client is None:
                return {"error": "Lightning client not available", "status": "error"}
                
            balance = ln_client.get_wallet_balance()
            return balance
        except Exception as e:
            error_msg = f"Error getting wallet balance: {str(e)}"
            if ctx:
                ctx.error(error_msg)
            return {"error": error_msg, "status": "error"}
    
    # Add resources
    @server.resource("resource://lightning/node/info")
    def get_node_info() -> Dict:
        """Get basic information about the Lightning node."""
        global _config
        if _config is None:
            _config = load_config()
        
        try:
            ln_client = get_ln_client()
            
            # Basic info
            node_info = {
                "implementation": _config["lightning"]["implementation"],
                "version": _config["server"]["mcp_version"],
                "status": "ok"
            }
            
            # Add network info
            try:
                node_info["network"] = _config["lightning"]["connection"][_config["lightning"]["implementation"]]["network"]
            except (KeyError, TypeError):
                node_info["network"] = "unknown"
            
            # Add channel info if available
            if ln_client is not None and hasattr(ln_client, "list_channels"):
                try:
                    channels = ln_client.list_channels()
                    node_info["channels"] = len(channels) if channels else 0
                except Exception:
                    node_info["channels"] = 0
            else:
                node_info["channels"] = 0
                
            return node_info
        except Exception as e:
            return {
                "implementation": "unknown",
                "network": "unknown",
                "version": "unknown",
                "channels": 0,
                "status": f"error: {str(e)}"
            }
    
    return server, host, port

def main():
    """Run the MCP server."""
    server, host, port = init_server()
    
    print(f"Starting Lightning MCP server on {host}:{port}")
    print(f"Server will be available to Cursor at: http://{host}:{port}/sse")
    
    # Run the server with SSE transport
    server.run(transport="sse")

if __name__ == "__main__":
    main()
