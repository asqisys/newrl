from pydantic import BaseModel
from typing import List


class TransactionsRequest(BaseModel):
    transaction_codes: List[str] = []

class BlockRequest(BaseModel):
    block_indexes: List[str] = []

class BlockAdditionRequest(BaseModel):
    block: dict
