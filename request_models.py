from pydantic import BaseModel
from enum import Enum


class BalanceType(Enum):
    TOKEN_IN_WALLET = 'TOKEN_IN_WALLET'
    ALL_TOKENS_IN_WALLET = 'ALL_TOKENS_IN_WALLET'
    ALL_WALLETS_FOR_TOKEN = 'ALL_WALLETS_FOR_TOKEN'


class BalanceRequest(BaseModel):
    balance_type: BalanceType = BalanceType.TOKEN_IN_WALLET
    token_code: str = None
    wallet_address: str = None


class TransferType(Enum):
    TYPE4 = 'TYPE4'
    TYPE5 = 'TYPE5'


class TransferRequest(BaseModel):
    transfer_type: TransferType = TransferType.TYPE4
    asset1_code: str
    asset2_code: str
    wallet1_address: str
    wallet2_address: str
    asset1_qty: float
    asset2_qty: float