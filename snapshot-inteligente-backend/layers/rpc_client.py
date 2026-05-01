import requests
import json
from typing import Any, List, Optional, Dict
from config import config
from models.errors import RPCConnectionError, RPCMethodError
import logging

logger = logging.getLogger(__name__)

class RPCClient:
    """
    Bitcoin Core RPC client.
    Handles connection, serialization, and error handling.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        timeout: int = None
    ):
        self.host = host or config.BITCOIN_RPC_HOST
        self.port = port or config.BITCOIN_RPC_PORT
        self.user = user or config.BITCOIN_RPC_USER
        self.password = password or config.BITCOIN_RPC_PASSWORD
        self.timeout = timeout or config.RPC_TIMEOUT_SECONDS
        self.url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password)
        self._session = requests.Session()
        self._session.auth = self.auth
    
    def call(self, method: str, params: List[Any] = None) -> dict:
        """
        Execute a Bitcoin RPC call.
        
        Args:
            method: RPC method name (e.g., 'getmempoolinfo')
            params: List of parameters or None
            
        Returns:
            Response data from Bitcoin Core
            
        Raises:
            RPCConnectionError: Network/connection issues
            RPCMethodError: RPC returns error response
        """
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        
        try:
            logger.debug(f"RPC call: {method} with params: {params}")
            response = self._session.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"RPC Connection failed: {e}")
            raise RPCConnectionError(f"Cannot connect to {self.url}: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"RPC Timeout: {e}")
            raise RPCConnectionError(f"RPC call timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            logger.error(f"RPC Request failed: {e}")
            raise RPCConnectionError(f"Request failed: {str(e)}")
        
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse RPC response: {e}")
            raise RPCConnectionError(f"Invalid JSON response: {str(e)}")
        
        # Check for JSON-RPC error
        if "error" in result and result["error"] is not None:
            error = result["error"]
            error_code = error.get("code", -1)
            error_msg = error.get("message", "Unknown error")
            logger.error(f"RPC error for {method}: [{error_code}] {error_msg}")
            raise RPCMethodError(method, error_code, error_msg)
        
        if "result" not in result:
            logger.error(f"Invalid RPC response format: {result}")
            raise RPCConnectionError("Invalid RPC response format")
        
        logger.debug(f"RPC response for {method}: success")
        return result["result"]
    
    def close(self):
        """Close the RPC session."""
        self._session.close()
