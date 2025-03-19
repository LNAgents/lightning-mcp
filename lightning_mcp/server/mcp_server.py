#!/usr/bin/env python
"""
Lightning MCP Server - Exposes Lightning Network functionality as MCP tools.
Using MCP SDK 1.4.1
"""
import json
import os
import sys
import logging
from typing import Dict, List, Optional, Any
import asyncio
import uvicorn

from fastmcp import FastMCP
from fastmcp.tools.base import Tool
from fastmcp.resources.base import Resource
from fastmcp.utilities.types import ImageContent as TextContent
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.routing import APIRoute
from sse_starlette.sse import EventSourceResponse

# Import Lightning Network client implementations
from lightning_mcp.lightning.lnd_client import LNDClient
from lightning_mcp.lightning.clightning_client import CLightningClient
from lightning_mcp.utils.config import get_config_with_validation

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_server.log')
    ]
)
logger = logging.getLogger("mcp-server")
logger.setLevel(logging.DEBUG)

class LightningMCPServer:
    """Main server class that handles MCP protocol and Lightning functionality."""
    
    def __init__(self):
        """Initialize the server with configuration."""
        self.config = get_config_with_validation()
        self.ln_client = None
        self.mcp_server = FastMCP(
            name=self.config.get("server", {}).get("mcp_name", "Lightning MCP"),
            protocol_version="2024-01-01",
            client_info={
                "name": "Lightning MCP Client",
                "version": self.config["server"]["mcp_version"]
            },
            capabilities={
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True},
                "prompts": {"listChanged": True},
                "logging": True,
                "roots": {"listChanged": True},
                "sampling": {
                    "enabled": True,
                    "sampleRate": 1.0
                }
            },
            port=self.config["server"]["port"]
        )
        self.setup_tools()
        
    def setup_tools(self):
        """Set up MCP tools."""
        @self.mcp_server.tool()
        async def create_invoice(amount: int, memo: Optional[str] = "", expiry: Optional[int] = 3600) -> str:
            """Create a Lightning Network invoice.
            
            Args:
                amount: Amount in satoshis
                memo: Optional memo
                expiry: Expiry time in seconds (default: 3600)
            """
            ln_client = self.get_ln_client()
            if ln_client is None:
                raise Exception("Lightning client not available")
            invoice = ln_client.create_invoice(amount, memo, expiry)
            return json.dumps(invoice)
        
        @self.mcp_server.tool()
        async def pay_invoice(payment_request: str, max_fee_percent: Optional[float] = 3.0) -> str:
            """Pay a Lightning Network invoice.
            
            Args:
                payment_request: BOLT11 invoice to pay
                max_fee_percent: Maximum fee as percentage of payment amount (default: 3.0)
            """
            ln_client = self.get_ln_client()
            if ln_client is None:
                raise Exception("Lightning client not available")
            payment = ln_client.pay_invoice(payment_request, max_fee_percent)
            return json.dumps(payment)
        
        @self.mcp_server.tool()
        async def check_payment(payment_hash: str) -> str:
            """Check the status of a Lightning Network payment.
            
            Args:
                payment_hash: Payment hash to check
            """
            ln_client = self.get_ln_client()
            if ln_client is None:
                raise Exception("Lightning client not available")
            payment_status = ln_client.check_payment(payment_hash)
            return json.dumps(payment_status)
        
        @self.mcp_server.tool()
        async def get_wallet_balance() -> str:
            """Get the current wallet balance."""
            ln_client = self.get_ln_client()
            if ln_client is None:
                raise Exception("Lightning client not available")
            balance = ln_client.get_wallet_balance()
            return json.dumps(balance)
    
    def get_ln_client(self):
        """Get or create Lightning client."""
        if self.ln_client is not None:
            return self.ln_client
            
        try:
            implementation = self.config["lightning"]["implementation"]
            logger.info(f"Initializing {implementation} client...")
            
            if implementation == "lnd":
                self.ln_client = LNDClient(self.config["lightning"]["connection"]["lnd"])
            elif implementation == "c-lightning":
                conn_config = self.config["lightning"]["connection"]["c-lightning"]
                self.ln_client = CLightningClient(conn_config)
            else:
                logger.error(f"Unsupported Lightning implementation: {implementation}")
                return None
                
            logger.info(f"Successfully initialized {implementation} client")
            return self.ln_client
        except Exception as e:
            logger.error(f"Error initializing Lightning client: {e}")
            return None
    
    async def handle_sse_connection(self, request: Request):
        """Handle SSE connections."""
        logger.info("New SSE connection request received")
        
        try:
            # Initialize Lightning client
            if self.get_ln_client() is None:
                return PlainTextResponse("Failed to initialize Lightning client", status_code=500)
            
            # Set up SSE response
            async def event_generator():
                try:
                    await self.mcp_server.run_sse_async()
                except Exception as e:
                    logger.error(f"Error in MCP server: {e}", exc_info=True)
                    yield {
                        "event": "error",
                        "data": str(e)
                    }
            
            return EventSourceResponse(event_generator())
            
        except Exception as e:
            logger.error(f"Error handling SSE connection: {e}")
            return PlainTextResponse(str(e), status_code=500)
    
    async def get_node_info(self) -> Dict:
        """Get basic information about the Lightning node."""
        try:
            ln_client = self.get_ln_client()
            
            # Basic info
            node_info = {
                "implementation": self.config["lightning"]["implementation"],
                "version": self.config["server"]["mcp_version"],
                "status": "ok"
            }
            
            # Add network info
            try:
                node_info["network"] = self.config["lightning"]["connection"][
                    self.config["lightning"]["implementation"]
                ]["network"]
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
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(
            title="Lightning MCP Server",
            description="Lightning Network MCP server exposing Lightning Network functionality as MCP tools",
            version=self.config["server"]["mcp_version"]
        )
        
        # Add SSE endpoint
        app.add_api_route("/sse", self.handle_sse_connection, methods=["GET"])
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            return {"status": "ok", "node_info": await self.get_node_info()}
        
        # Configure CORS for SSE
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Adjust in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        return app
    
    async def run(self):
        """Run the server."""
        host = self.config["server"]["host"]
        port = self.config["server"]["port"]
        
        logger.info(f"Starting Lightning MCP server on {host}:{port}")
        logger.info(f"Server will be available to Cursor at: http://{host}:{port}/sse")
        logger.info(f"API documentation available at: http://{host}:{port}/docs")
        
        # Initialize Lightning client
        if self.get_ln_client() is None:
            logger.error("Failed to initialize Lightning client")
            return
            
        # Run the FastMCP server
        await self.mcp_server.run_sse_server(host=host, port=port)

def main():
    """Run the MCP server."""
    server = LightningMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
