"""
Transaction builder for creating unsigned transactions.
Handles coin selection and transaction construction.
"""

import logging
from typing import List, Tuple, Optional
from layers.rpc_client import RPCClient

logger = logging.getLogger(__name__)


class UTXO:
    """Represents an unspent transaction output."""
    
    def __init__(self, txid: str, vout: int, amount: float, confirmations: int):
        self.txid = txid
        self.vout = vout
        self.amount = amount  # BTC
        self.confirmations = confirmations
        self.amount_sat = int(amount * 100_000_000)  # Convert to satoshis
    
    def __repr__(self):
        return f"UTXO({self.txid[:8]}...:{self.vout}, {self.amount} BTC, {self.confirmations} conf)"


class TransactionBuilder:
    """Builds unsigned transactions with coin selection."""
    
    @staticmethod
    def get_utxos(rpc_client: RPCClient, min_confirmations: int = 1) -> List[UTXO]:
        """
        Fetch available UTXOs from wallet.
        
        Args:
            rpc_client: RPC client instance
            min_confirmations: Minimum confirmations required
            
        Returns:
            List of UTXO objects
        """
        utxos_raw = rpc_client.call('listunspent', [min_confirmations])
        utxos = [
            UTXO(
                txid=u['txid'],
                vout=u['vout'],
                amount=u['amount'],
                confirmations=u['confirmations']
            )
            for u in utxos_raw
        ]
        logger.info(f"Found {len(utxos)} UTXOs")
        return utxos
    
    @staticmethod
    def select_utxos_automatic(
        utxos: List[UTXO],
        target_amount_sat: int,
        fee_sat: int
    ) -> Tuple[List[UTXO], int]:
        """
        Automatically select UTXOs using largest-first strategy.
        
        Args:
            utxos: Available UTXOs
            target_amount_sat: Target amount in satoshis
            fee_sat: Estimated fee in satoshis
            
        Returns:
            Tuple of (selected_utxos, change_amount_sat)
            
        Raises:
            ValueError: Insufficient UTXOs
        """
        required_sat = target_amount_sat + fee_sat
        selected = []
        total_sat = 0
        
        # Sort by amount (largest first)
        sorted_utxos = sorted(utxos, key=lambda u: u.amount_sat, reverse=True)
        
        for utxo in sorted_utxos:
            selected.append(utxo)
            total_sat += utxo.amount_sat
            if total_sat >= required_sat:
                break
        
        if total_sat < required_sat:
            raise ValueError(
                f"Insufficient balance: need {required_sat} sat, have {total_sat} sat"
            )
        
        change_sat = total_sat - target_amount_sat - fee_sat
        logger.info(f"Selected {len(selected)} UTXOs, change: {change_sat} sat")
        return selected, change_sat
    
    @staticmethod
    def select_utxos_manual(
        utxos: List[UTXO],
        selected_indices: List[int],
        target_amount_sat: int,
        fee_sat: int
    ) -> Tuple[List[UTXO], int]:
        """
        Select specific UTXOs by index.
        
        Args:
            utxos: Available UTXOs
            selected_indices: Indices of UTXOs to use
            target_amount_sat: Target amount in satoshis
            fee_sat: Estimated fee in satoshis
            
        Returns:
            Tuple of (selected_utxos, change_amount_sat)
            
        Raises:
            ValueError: Invalid indices or insufficient amount
        """
        if not selected_indices:
            raise ValueError("No UTXOs selected")
        
        selected = []
        total_sat = 0
        
        for idx in selected_indices:
            if idx < 0 or idx >= len(utxos):
                raise ValueError(f"Invalid UTXO index: {idx}")
            selected.append(utxos[idx])
            total_sat += utxos[idx].amount_sat
        
        required_sat = target_amount_sat + fee_sat
        if total_sat < required_sat:
            raise ValueError(
                f"Selected UTXOs insufficient: need {required_sat} sat, have {total_sat} sat"
            )
        
        change_sat = total_sat - target_amount_sat - fee_sat
        logger.info(f"Selected {len(selected)} UTXOs manually, change: {change_sat} sat")
        return selected, change_sat
    
    @staticmethod
    def create_unsigned_transaction(
        rpc_client: RPCClient,
        recipient: str,
        amount_btc: float,
        fee_rate_sat_vB: float,
        utxo_selection_mode: str = "automatic",
        selected_utxo_indices: Optional[List[int]] = None,
        change_address: Optional[str] = None
    ) -> dict:
        """
        Create an unsigned transaction.
        
        Args:
            rpc_client: RPC client instance
            recipient: Recipient Bitcoin address
            amount_btc: Amount to send in BTC
            fee_rate_sat_vB: Fee rate in sat/vB
            utxo_selection_mode: "automatic" or "manual"
            selected_utxo_indices: UTXO indices for manual selection
            change_address: Custom change address (uses first change address if not provided)
            
        Returns:
            Dict with transaction details
            
        Raises:
            ValueError: Invalid parameters or insufficient funds
        """
        logger.info(f"Creating unsigned TX: {amount_btc} BTC to {recipient[:20]}... at {fee_rate_sat_vB} sat/vB")
        
        # Validate recipient address
        try:
            addr_info = rpc_client.call('getaddressinfo', [recipient])
            if not addr_info.get('isvalid'):
                raise ValueError(f"Invalid address: {recipient}")
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            raise ValueError(f"Invalid address: {recipient}")
        
        # Get UTXOs
        utxos = TransactionBuilder.get_utxos(rpc_client)
        if not utxos:
            raise ValueError("No UTXOs available")
        
        # Convert amount to satoshis
        amount_sat = int(amount_btc * 100_000_000)
        
        # Estimate fee (rough estimate: 250 vBytes for typical TX)
        estimated_vbytes = 250
        fee_sat = int(fee_rate_sat_vB * estimated_vbytes)
        
        # Select UTXOs
        if utxo_selection_mode == "manual":
            if not selected_utxo_indices:
                raise ValueError("Manual mode requires selected_utxo_indices")
            selected_utxos, change_sat = TransactionBuilder.select_utxos_manual(
                utxos, selected_utxo_indices, amount_sat, fee_sat
            )
        else:  # automatic
            selected_utxos, change_sat = TransactionBuilder.select_utxos_automatic(
                utxos, amount_sat, fee_sat
            )
        
        # Get change address if not provided
        if not change_address:
            change_address = rpc_client.call('getrawchangeaddress')
        
        # Build inputs and outputs
        inputs = [
            {"txid": u.txid, "vout": u.vout}
            for u in selected_utxos
        ]
        
        outputs = {
            recipient: amount_btc,
            change_address: (change_sat / 100_000_000)  # Convert back to BTC
        }
        
        # Create raw transaction
        tx_hex = rpc_client.call('createrawtransaction', [inputs, outputs])
        
        return {
            "tx_hex": tx_hex,
            "inputs": inputs,
            "outputs": outputs,
            "selected_utxos": len(selected_utxos),
            "change_amount_sat": change_sat,
            "estimated_fee_sat": fee_sat,
            "recipient": recipient,
            "amount_sat": amount_sat
        }
