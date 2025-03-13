#!/usr/bin/env python
"""
Example MCP client demonstrating how to connect to the Lightning MCP server.
"""
import asyncio
import sys
from typing import Dict, List, Any

from fastmcp import MCPClient

async def main():
    """Run the example MCP client."""
    # Connect to the Lightning MCP server
    client = MCPClient("localhost", 8080)
    
    try:
        # Connect to the server
        await client.connect()
        print("Connected to Lightning MCP server")
        
        # List available tools
        print("\n--- Available Lightning Network Tools ---")
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool: {tool['name']}")
            print(f"  Description: {tool['description']}")
            print(f"  Parameters: {tool['parameters']}")
            print()
        
        # Create an invoice
        print("\n--- Creating a Lightning Invoice ---")
        invoice_result = await client.call_tool(
            "create_invoice",
            {
                "amount_sat": 1000,
                "memo": "Example MCP client payment",
                "expiry": 3600
            }
        )
        print(f"Invoice created: {invoice_result}")
        
        # Check wallet balance
        print("\n--- Checking Wallet Balance ---")
        balance = await client.call_tool("get_wallet_balance", {})
        print(f"Wallet balance: {balance}")
        
        # List channels
        print("\n--- Listing Lightning Channels ---")
        channels = await client.call_tool("list_channels", {})
        print(f"Number of channels: {len(channels)}")
        for channel in channels:
            print(f"Channel with {channel['remote_pubkey']}")
            print(f"  Capacity: {channel['capacity']} sats")
            print(f"  Local balance: {channel['local_balance']} sats")
            print(f"  Remote balance: {channel['remote_balance']} sats")
            print(f"  Active: {channel['active']}")
            print()
        
        # Pay the invoice we just created
        print("\n--- Paying the Lightning Invoice ---")
        payment_result = await client.call_tool(
            "pay_invoice",
            {
                "payment_request": invoice_result["payment_request"]
            }
        )
        print(f"Payment result: {payment_result}")
        
        # Check payment status
        print("\n--- Checking Payment Status ---")
        payment_status = await client.call_tool(
            "check_payment_status",
            {
                "payment_hash": invoice_result["payment_hash"]
            }
        )
        print(f"Payment status: {payment_status}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Disconnect from the server
        await client.disconnect()
        print("\nDisconnected from Lightning MCP server")

if __name__ == "__main__":
    # Run the example client
    asyncio.run(main()) 