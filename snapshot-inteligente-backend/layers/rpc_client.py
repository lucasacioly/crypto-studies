import requests
import json
from typing import Any, List, Optional, Dict
from config import config
from models.errors import RPCConnectionError, RPCMethodError
import logging
import time

logger = logging.getLogger(__name__)

class RPCClient:
    """
    Bitcoin Core RPC client.
    Handles connection, serialization, and error handling.
    Supports multiple wallets via /wallet/WALLET_NAME endpoints.
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
        self.selected_wallet: Optional[str] = None
    
    def call(self, method: str, params: List[Any] = None, wallet: Optional[str] = None) -> dict:
        """
        Execute a Bitcoin RPC call.
        
        Args:
            method: RPC method name (e.g., 'getmempoolinfo')
            params: List of parameters or None
            wallet: Wallet name for wallet-specific calls. If None, uses selected_wallet if available.
            
        Returns:
            Response data from Bitcoin Core
            
        Raises:
            RPCConnectionError: Network/connection issues
            RPCMethodError: RPC returns error response
        """
        if params is None:
            params = []
        
        # Use provided wallet or selected wallet
        wallet_to_use = wallet or self.selected_wallet
        url = self.url
        if wallet_to_use:
            url = f"{self.url}/wallet/{wallet_to_use}"
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        
        try:
            logger.debug(f"RPC call: {method} with params: {params} (wallet: {wallet_to_use or 'none'})")
            response = self._session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"RPC Connection failed: {e}")
            raise RPCConnectionError(f"Cannot connect to {url}: {str(e)}")
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
    
    def select_wallet(self, wallet_name: str) -> None:
        """Select a wallet for subsequent calls."""
        self.selected_wallet = wallet_name
        logger.info(f"Selected wallet: {wallet_name}")
    
    def get_selected_wallet(self) -> Optional[str]:
        """Get the currently selected wallet."""
        return self.selected_wallet
    
    def list_wallets(self) -> List[str]:
        """List all loaded wallets."""
        return self.call('listwallets')
    
    def list_wallet_dir(self) -> dict:
        """List all wallet directories."""
        return self.call('listwalletdir')
    
    def load_wallet(self, wallet_name: str) -> dict:
        """Load a wallet if not already loaded."""
        try:
            return self.call('loadwallet', [wallet_name])
        except RPCMethodError as e:
            if "already loaded" in str(e):
                logger.info(f"Wallet {wallet_name} already loaded")
                return {"name": wallet_name, "warning": "already loaded"}
            raise
    
    def estimate_smart_fee(self, target_blocks: int = 2) -> dict:
        """
        Estimate smart fee using Bitcoin Core.
        
        Args:
            target_blocks: Target number of blocks (1-1008)
            
        Returns:
            Dict with fee_rate (BTC/kB) and warnings
        """
        return self.call('estimatesmartfee', [target_blocks])
    
    def estimate_fee_sat_vB(self, target_blocks: int = 2) -> float:
        """
        Estimate fee in sat/vB using Bitcoin Core.
        
        Args:
            target_blocks: Target number of blocks
            
        Returns:
            Fee rate in sat/vB (satoshis per virtual byte)
        """
        estimate = self.estimate_smart_fee(target_blocks)
        fee_btc_per_kb = estimate.get('feerate', 0.0001)
        # Convert BTC/kB to sat/vB: (BTC * 1e8 sat/BTC) / (1000 bytes)
        fee_sat_vB = (fee_btc_per_kb * 100_000_000) / 1000
        return fee_sat_vB
    
    def close(self):
        """Close the RPC session."""
        self._session.close()
