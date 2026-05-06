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


class TransactionCreateRequest(BaseModel):
    """Request to create unsigned transaction."""
    recipient: str = Field(..., description="Recipient Bitcoin address")
    amount_btc: float = Field(..., gt=0, description="Amount to send in BTC")
    fee_rate_sat_vB: float = Field(..., gt=0, description="Fee rate in sat/vB")
    utxo_selection_mode: str = Field("automatic", description="'automatic' or 'manual'")
    selected_utxo_indices: Optional[List[int]] = Field(None, description="UTXO indices for manual selection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "bcrt1...",
                "amount_btc": 0.001,
                "fee_rate_sat_vB": 5.5,
                "utxo_selection_mode": "automatic"
            }
        }


class TransactionCreateResponse(BaseModel):
    """Response from transaction creation."""
    tx_hex: str = Field(..., description="Unsigned transaction hex")
    inputs: List[dict] = Field(..., description="Transaction inputs")
    outputs: dict = Field(..., description="Transaction outputs")
    selected_utxos: int = Field(..., description="Number of UTXOs selected")
    change_amount_sat: int = Field(..., description="Change amount in satoshis")
    estimated_fee_sat: int = Field(..., description="Estimated fee in satoshis")
    recipient: str = Field(..., description="Recipient address")
    amount_sat: int = Field(..., description="Amount to send in satoshis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tx_hex": "0200000001...",
                "inputs": [{"txid": "abc...", "vout": 0}],
                "outputs": {"bcrt1...": 0.001, "bcrt1...": 0.099},
                "selected_utxos": 1,
                "change_amount_sat": 9900000,
                "estimated_fee_sat": 100000,
                "recipient": "bcrt1...",
                "amount_sat": 100000
            }
        }


class TransactionSignRequest(BaseModel):
    """Request to sign transaction."""
    tx_hex: str = Field(..., description="Unsigned transaction hex")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tx_hex": "0200000001..."
            }
        }


class TransactionSignResponse(BaseModel):
    """Response from transaction signing."""
    tx_hex: str = Field(..., description="Signed transaction hex")
    complete: bool = Field(..., description="Whether signing was complete")
    errors: List[str] = Field(default_factory=list, description="Signing errors if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tx_hex": "02000000010123...",
                "complete": True,
                "errors": []
            }
        }


class TransactionBroadcastRequest(BaseModel):
    """Request to broadcast signed transaction."""
    tx_hex: str = Field(..., description="Signed transaction hex")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tx_hex": "02000000010123..."
            }
        }


class TransactionBroadcastResponse(BaseModel):
    """Response from broadcasting."""
    txid: str = Field(..., description="Transaction ID")
    wallet: str = Field(..., description="Wallet that sent the transaction")
    status: str = Field(..., description="Transaction status")
    broadcast_time: str = Field(..., description="ISO timestamp of broadcast")
    
    class Config:
        json_schema_extra = {
            "example": {
                "txid": "abc123...",
                "wallet": "wallet1",
                "status": "broadcast",
                "broadcast_time": "2026-05-06T12:00:00Z"
            }
        }


class UTXOInfo(BaseModel):
    """Information about an UTXO."""
    index: int = Field(..., description="UTXO index in list")
    txid: str = Field(..., description="Previous transaction ID")
    vout: int = Field(..., description="Previous output index")
    amount_btc: float = Field(..., description="Amount in BTC")
    amount_sat: int = Field(..., description="Amount in satoshis")
    confirmations: int = Field(..., description="Number of confirmations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "index": 0,
                "txid": "abc...",
                "vout": 0,
                "amount_btc": 0.1,
                "amount_sat": 10000000,
                "confirmations": 5
            }
        }


class UTXOListResponse(BaseModel):
    """List of available UTXOs."""
    wallet: str = Field(..., description="Wallet name")
    utxos: List[UTXOInfo] = Field(..., description="Available UTXOs")
    total_amount_sat: int = Field(..., description="Total amount available in satoshis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "wallet": "wallet1",
                "utxos": [
                    {
                        "index": 0,
                        "txid": "abc...",
                        "vout": 0,
                        "amount_btc": 0.1,
                        "amount_sat": 10000000,
                        "confirmations": 5
                    }
                ],
                "total_amount_sat": 10000000
            }
        }


class FeeEstimateResponse(BaseModel):
    """Fee rate estimation response."""
    fee_rate_sat_vB: float = Field(..., description="Estimated fee rate in sat/vB")
    source: str = Field(..., description="Source of estimate: 'bitcoin_core' or 'manual'")
    target_blocks: int = Field(..., description="Target number of blocks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fee_rate_sat_vB": 5.5,
                "source": "bitcoin_core",
                "target_blocks": 2
            }
        }


class SentTransaction(BaseModel):
    """Record of a sent transaction."""
    txid: str = Field(..., description="Transaction ID")
    wallet: str = Field(..., description="Wallet that sent it")
    recipient: str = Field(..., description="Recipient address")
    amount_btc: float = Field(..., description="Amount sent in BTC")
    fee_sat: int = Field(..., description="Fee paid in satoshis")
    status: str = Field(..., description="Transaction status")
    created_at: str = Field(..., description="ISO timestamp when created")
    broadcast_at: str = Field(..., description="ISO timestamp when broadcast")
    confirmations: int = Field(default=0, description="Number of confirmations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "txid": "abc...",
                "wallet": "wallet1",
                "recipient": "bcrt1...",
                "amount_btc": 0.001,
                "fee_sat": 1000,
                "status": "broadcast",
                "created_at": "2026-05-06T12:00:00Z",
                "broadcast_at": "2026-05-06T12:00:01Z",
                "confirmations": 0
            }
        }
