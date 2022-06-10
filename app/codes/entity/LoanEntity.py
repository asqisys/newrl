from sqlalchemy import Column, Integer, String, Float

from app.codes.entity.BaseEntity import BaseEntity


class LoanEntity(BaseEntity):
    __tablename__ = 'loan'
    id = Column(Integer, primary_key=True)
    borrower = Column(String)
    lender = Column(String)
    amount = Column(Float)
    def __repr__(self):
       return "<User(borrower='%s', lender='%s', amount='%f')>" % (
                            self.name, self.fullname, self.nickname)
    def belongsToContract(self):
        return ["LoanContract"]

