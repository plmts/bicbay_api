import enum
from sqlalchemy import Column, Integer, String, Numeric, Enum, create_engine, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class UserType(enum.Enum):
  COSTUMER = 'costumer'
  RETAILER = 'retailer'

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(50), nullable=False)
  cpf = Column(String(11), unique=True, nullable=True)
  cnpj = Column(String(15), unique=True, nullable=True)
  email = Column(String, unique=True, nullable=False)
  password = Column(String, nullable=False)
  amount = Column(Numeric(precision=10, scale=2), default=1000.00)
  user_type = Column(Enum(UserType), nullable=False)

  __table_args__ = (
      UniqueConstraint('cpf', 'user_type', name='unique_costumer_cpf'),
      UniqueConstraint('cnpj', 'user_type', name='unique_retailer_cnpj'),
  )

class Transfer(Base):
  __tablename__ = 'transfers'
  id = Column(Integer, primary_key=True, autoincrement=True)
  payer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  payee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  value = Column(Numeric(precision=10, scale=2), nullable=False)

  payer = relationship("User", foreign_keys=[payer_id])
  payee = relationship("User", foreign_keys=[payee_id])

# Configuração do banco de dados
engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()