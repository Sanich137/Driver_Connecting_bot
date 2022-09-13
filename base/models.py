from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger, Boolean, sql, PrimaryKeyConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True, unique=True)
    first_name = Column(String(50))
    username = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10))
    role = Column(Integer(), ForeignKey('roles.id'))
    updated = Column(DateTime())
    phone = Column(String(12))
    email = Column(String(50))
    cars = relationship("Car", backref="users")


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer(), primary_key=True, unique=True, autoincrement=True)
    gos_reg_znak = Column(String(100)) ## x111xx777
    inserted_date = Column(DateTime())
    is_reacheble = Column(Boolean())
    is_deleted = Column(Boolean())
    link_photo_id = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=False)


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True, unique=True)
    role_type = Column(String(100))
