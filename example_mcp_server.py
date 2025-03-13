#!/usr/bin/env python
"""
Example MCP Server - Using the official MCP SDK instead of fastmcp
"""
import json
import os
import sys
from typing import Dict, Optional

# Import the official MCP SDK
from mcp.server import Server
from mcp.types import Tool, Resource

# Create an MCP server
server = Server(name="Lightning MCP Example")

# Define functions for our lightning tools
async def create_invoice_impl(amount_sat: int, memo: Optional[str] = None, expiry: int = 3600) -> Dict:
    """
    Create a Lightning Network invoice for the specified amount.
    
    Args:
        amount_sat: Amount in satoshis
        memo: Optional description for the invoice
        expiry: Expiry time in seconds (default: 1 hour)
        
    Returns:
        Dictionary with invoice details including payment_request (bolt11 invoice)
    """
    # Simple implementation for demonstration
    print(f"Creating invoice for {amount_sat} sats with memo: {memo}", file=sys.stderr)
    
    # Return a simulated invoice
    return {
        "payment_hash": "simulated_hash",
        "payment_request": f"lnbc{amount_sat}p1fakelnxyz",
        "amount_sat": amount_sat,
        "memo": memo or "",
        "expiry": expiry,
    }

async def get_wallet_balance_impl() -> Dict:
    """
    Get the current wallet balance.
    
    Returns:
        Dictionary with balance information
    """
    # Simple implementation for demonstration
    print("Getting wallet balance", file=sys.stderr)
    
    # Return a simulated balance
    return {
        "total_balance": 1000000,
        "confirmed_balance": 950000,
        "unconfirmed_balance": 50000,
    }

async def get_node_info_impl() -> Dict:
    """
    Get information about the Lightning node.
    
    Returns:
        Dictionary with node information
    """
    return {
        "node_pubkey": "simulated_pubkey",
        "node_alias": "Example Lightning Node",
        "num_active_channels": 5,
        "num_inactive_channels": 1,
        "version": "0.11.0",
        "network": "mainnet",
    }

# Register the tools with the server
async def register_tools():
    # Create invoice tool
    invoice_tool = Tool(
        name="create_invoice",
        description="Create a Lightning Network invoice for the specified amount",
        inputSchema={
            "type": "object",
            "properties": {
                "amount_sat": {"type": "integer", "description": "Amount in satoshis"},
                "memo": {"type": "string", "description": "Optional description for the invoice"},
                "expiry": {"type": "integer", "description": "Expiry time in seconds (default: 1 hour)"},
            },
            "required": ["amount_sat"],
        },
    )
    
    # Wallet balance tool
    balance_tool = Tool(
        name="get_wallet_balance",
        description="Get the current wallet balance",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    )
    
    # Register the tools
    server.register_tool_handler("create_invoice", create_invoice_impl)
    server.register_tool(invoice_tool)
    
    server.register_tool_handler("get_wallet_balance", get_wallet_balance_impl)
    server.register_tool(balance_tool)
    
    # Register node info resource
    node_info_resource = Resource(
        uri="resource://lightning/info",
        name="Lightning Node Information",
        description="Basic information about the Lightning node",
        mimeType="application/json",
    )
    
    server.register_resource_handler("resource://lightning/info", get_node_info_impl)
    server.register_resource(node_info_resource)

if __name__ == "__main__":
    import asyncio
    import argparse
    
    parser = argparse.ArgumentParser(description="Lightning MCP Example Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to listen on")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()
    
    print(f"Starting Lightning MCP Example server on {args.host}:{args.port}", file=sys.stderr)
    print("Use Ctrl+C to stop the server", file=sys.stderr)
    
    # Set up tools and resources
    asyncio.run(register_tools())
    
    # Run the server using SSE transport
    asyncio.run(server.run_sse_server(host=args.host, port=args.port)) 