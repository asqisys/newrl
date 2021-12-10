from pydantic import BaseModel
from typing import List


class TransactionsRequest(BaseModel):
    transaction_codes: List[str] = []
