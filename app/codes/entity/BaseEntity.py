from abc import abstractmethod

from app.codes.base.Base import Base


class BaseEntity(Base):
    __abstract__=True
    def __repr__(self):
       return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                            self.name, self.fullname, self.nickname)
    @abstractmethod
    def belongsToContract(self):
        return self.__class__.__name__



        # CRUD
        # UPDATE
        # CREATE
        # SOFT DELETE
        # READ
        # Belonsto A B fk A get attr -
        # Read plus join query fire