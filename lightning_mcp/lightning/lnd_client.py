#!/usr/bin/env python
"""
LND client implementation using REST API.
"""
import json
import logging
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class LNDClient:
    """Client for interacting with LND via REST API."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        tls_cert_path: str = "tls.cert",
        macaroon_path: str = "admin.macaroon",
        network: str = "mainnet"
    ):
        """Initialize the LND client.
        
        Args:
            host: LND host address
            port: LND REST API port
            tls_cert_path: Path to TLS certificate
            macaroon_path: Path to admin macaroon
            network: Network type (mainnet, testnet, regtest)
        """
        self.host = host
        self.port = port
        self.tls_cert_path = Path(tls_cert_path)
        self.macaroon_path = Path(macaroon_path)
        self.network = network
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = str(self.tls_cert_path)
        
        # Read macaroon
        try:
            with open(self.macaroon_path, 'rb') as f:
                macaroon = f.read().hex()
                self.session.headers.update({
                    'Grpc-Metadata-macaroon': macaroon
                })
        except Exception as e:
            logger.error(f"Failed to read macaroon: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a request to the LND REST API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data (optional)
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_info(self) -> Dict:
        """Get node information."""
        return self._make_request("GET", "/v1/getinfo")
    
    def list_channels(self) -> List[Dict]:
        """List all channels."""
        response = self._make_request("GET", "/v1/channels")
        return response.get("channels", [])
    
    def create_invoice(self, amount_sats: int, memo: str = "") -> Dict:
        """Create a new invoice.
        
        Args:
            amount_sats: Amount in satoshis
            memo: Invoice memo (optional)
            
        Returns:
            Invoice details
        """
        data = {
            "value": str(amount_sats),
            "memo": memo
        }
        return self._make_request("POST", "/v1/invoices", data)
    
    def pay_invoice(self, payment_request: str) -> Dict:
        """Pay an invoice.
        
        Args:
            payment_request: BOLT11 payment request
            
        Returns:
            Payment details
        """
        data = {
            "payment_request": payment_request
        }
        return self._make_request("POST", "/v1/channels/transactions", data)
    
    def get_balance(self) -> Dict:
        """Get wallet balance."""
        return self._make_request("GET", "/v1/balance/blockchain")
    
    def get_channel_balance(self) -> Dict:
        """Get channel balance."""
        return self._make_request("GET", "/v1/balance/channels")
