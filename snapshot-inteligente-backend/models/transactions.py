"""
Transaction models for Tarefa 3 (Task 3).
Includes transaction status interpretation and wallet context.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class TransactionStatus(str, Enum):
    """Transaction status enum."""
    BROADCAST = "broadcast"
    MEMPOOL = "mempool"
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"


class TransactionInterpretation(BaseModel):
    """Interpretation of transaction state."""
    status: TransactionStatus = Field(..., description="Current transaction status")
    message: str = Field(..., description="Human-readable message about the transaction")
    warning: Optional[str] = Field(None, description="Warning if transaction is delayed or problematic")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "mempool",
                "message": "Transação aceita na mempool, aguardando inclusão em bloco.",
                "warning": "Transação está na mempool há mais de 2 minutos."
            }
        }


class TransactionDetail(BaseModel):
    """Detailed transaction information with interpretation."""
    txid: str = Field(..., description="Transaction ID")
    wallet: str = Field(..., description="Wallet that created/owns this transaction")
    status: TransactionStatus = Field(..., description="Transaction status")
    confirmed: bool = Field(..., description="Whether transaction is confirmed")
    confirmations: int = Field(..., description="Number of confirmations")
    block_hash: Optional[str] = Field(None, description="Block hash if confirmed")
    age_seconds: int = Field(..., description="Age of transaction in seconds")
    message: str = Field(..., description="Interpretation message")
    warning: Optional[str] = Field(None, description="Warning if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "txid": "abc123...",
                "wallet": "wallet1",
                "status": "mempool",
                "confirmed": False,
                "confirmations": 0,
                "block_hash": None,
                "age_seconds": 145,
                "message": "Transação aceita na mempool, aguardando inclusão em bloco.",
                "warning": "Transação está na mempool há mais de 2 minutos."
            }
        }


class WalletInfo(BaseModel):
    """Wallet information."""
    walletname: str = Field(..., description="Wallet name")
    balance: float = Field(..., description="Wallet balance in BTC")
    txcount: int = Field(..., description="Number of transactions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "walletname": "wallet1",
                "balance": 0.001,
                "txcount": 4
            }
        }


class WalletStatus(BaseModel):
    """Wallet status information."""
    wallet: str = Field(..., description="Selected wallet name")
    balance: float = Field(..., description="Wallet balance in BTC")
    utxos: int = Field(..., description="Number of available UTXOs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "wallet": "wallet1",
                "balance": 0.0012,
                "utxos": 3
            }
        }


class WalletListResponse(BaseModel):
    """Response for wallet listing."""
    available_wallets: List[str] = Field(..., description="All available wallets in the node")
    loaded_wallets: List[str] = Field(..., description="Currently loaded wallets")
    selected_wallet: Optional[str] = Field(None, description="Currently selected wallet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "available_wallets": ["wallet1", "wallet2"],
                "loaded_wallets": ["wallet1"],
                "selected_wallet": "wallet1"
            }
        }


class WalletSelectResponse(BaseModel):
    """Response for wallet selection."""
    selected_wallet: str = Field(..., description="Name of selected wallet")
    wallet_info: WalletInfo = Field(..., description="Information about selected wallet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "selected_wallet": "wallet2",
                "wallet_info": {
                    "walletname": "wallet2",
                    "balance": 0.001,
                    "txcount": 4
                }
            }
        }
