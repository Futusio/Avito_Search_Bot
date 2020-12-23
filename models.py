from sqlalchemy import Column, Integer, String, create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///main.db', echo=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    message_id = Column(Integer)
    region = Column(String)

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
    
    def __repr__(self):
        return "<User {} with name {}".format(self.user_id, self.name)


if __name__ == "__main__":
    answer = input("Create new table (y/n)?: ")
    if answer == 'y':
        metadata = MetaData()

        user_table = Table('users', metadata,
                Column('user_id', Integer, primary_key=True),
                Column('name', String),
                Column('message_id', Integer),
                Column('region', String))    

        metadata.create_all(engine)
        print("Success")