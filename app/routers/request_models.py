from pydantic import BaseModel
from enum import Enum
from typing import List, Optional


class BalanceType(Enum):
    TOKEN_IN_WALLET = 'TOKEN_IN_WALLET'
    ALL_TOKENS_IN_WALLET = 'ALL_TOKENS_IN_WALLET'
    ALL_WALLETS_FOR_TOKEN = 'ALL_WALLETS_FOR_TOKEN'


class BalanceRequest(BaseModel):
    balance_type: BalanceType = BalanceType.TOKEN_IN_WALLET
    token_code: str = 't0021'
    wallet_address: str = '0x762485963e99f6a6548729f11d610dd37ffd3b73'


class TransferType(int, Enum):
    TYPE4 = 4
    TYPE5 = 5


class TransferRequest(BaseModel):
    transfer_type: TransferType = TransferType.TYPE4
    asset1_code: str = 't0012'
    asset2_code: str = 't0023'
    wallet1_address: str = '0x762485963e99f6a6548729f11d610dd37ffd3b73'
    wallet2_address: str = '0x9b85fcc6071cb974458ce9d2260fd1f102760f8b'
    asset1_qty: float = 100.0
    asset2_qty: float = 0

class CreateTokenRequest(BaseModel):
    token_name: str = "NEWTOKEN"
    tokencode: str
    token_type: str
    first_owner: str = '0x762485963e99f6a6548729f11d610dd37ffd3b73'
    custodian: str = '0x762485963e99f6a6548729f11d610dd37ffd3b73'
    legal_doc: str = '686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401'
    amount_created: int = 1000000
    value_created: int = 10000
    disallowed_regions: Optional[List[str]] = []
    is_smart_contract_token: bool = False
    token_attributes: dict

class KYCDoc(BaseModel):
    type: int
    hash: str

class CreateWalletRequest(BaseModel):
    custodian_address: str = '0x762485963e99f6a6548729f11d610dd37ffd3b73'
    ownertype: str = "1"
    jurisdiction: str = "910"
    kyc_docs: List[KYCDoc] = [{'type': 1, 'hash': '686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401'}]
    specific_data: dict


class AddWalletRequest(BaseModel):
    custodian_address: str = '0x762485963e99f6a6548729f11d610dd37ffd3b73'
    ownertype: str = "1"
    jurisdiction: str = "910"
    kyc_docs: List[KYCDoc] = [{'type': 1, 'hash': '686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401'}]
    specific_data: dict
    public_key: str


class TransactionsRequest(BaseModel):
    transaction_codes: List[str] = []


class BlockRequest(BaseModel):
    block_indexes: List[str] = []


class BlockAdditionRequest(BaseModel):
    block: dict


class ReceiptAdditionRequest(BaseModel):
    receipt: dict
