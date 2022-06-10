from sqlalchemy import create_engine

from app.codes.base.Base import get_session

class ScStateUpdater:
    def updateState(self, state):
        # who is calling it, do they have state type in thier schema
        print(self.__class__.__name__)
        for i in state.belongsToContract():
            print(i.__class__.__name__)
            if (i == self.__class__.__name__):
                get_session().add(state)
                get_session().commit()
                return True
        print("Entity Belongs to different Contracts ", state.belongsToContract())




