class BitcoinServiceError(Exception):
    """Base exception for all Bitcoin service errors."""
    pass

class RPCConnectionError(BitcoinServiceError):
    """Raised when RPC connection fails."""
    def __init__(self, message: str, retries: int = 0):
        self.message = message
        self.retries = retries
        super().__init__(f"RPC Connection Error (attempts: {retries}): {message}")

class RPCMethodError(BitcoinServiceError):
    """Raised when RPC method returns error."""
    def __init__(self, method: str, error_code: int, error_message: str):
        self.method = method
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f"RPC Method '{method}' failed: [{error_code}] {error_message}")
