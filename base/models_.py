# Todo Модели базы данных Человек, Его Подписка, переписка. Видимо, сначала сделать структуру как в выдаче,
#  потом пересобрать
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, LargeBinary, Numeric, SmallInteger, Boolean, sql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()


# Таблица подписки
class Subscription(Base):
    __tablename__ = 'subscriptions'
    uid = Column(Integer(), primary_key=True, unique=True)
    id = Column(Integer(), primary_key=False, unique=True)
    name = Column(String(50))
    price = Column(Integer())
    updated = Column(DateTime(), default=None)
    subscriptionServiceMap = Column(String(10))
    number = Column(String(15))
    type = Column(Integer(), primary_key=False, unique=False)
    inserted = Column(DateTime(), default=None)
    paymentDate = Column(DateTime(), default=None)
    endDate = Column(DateTime() or None)
    status = Column(String(15))
    customerId = Column(String(40))
    supplierId = Column(String(40))
    chatRoomId = Column(String(40))
    lastMessageTime = Column(DateTime(), default=None)
    unreadMessageCount = Column(Integer(), primary_key=False, unique=False)
    senderUUID = Column(String(40))
    lastName = Column(String(40), default=None)  # "КЛИНКОВ"
    firstName = Column(String(40), default=None)  # "ВИТАЛИЙ"
    middleName = Column(String(40), default=None)  # "ЮРЬЕВИЧ"
    chat_messages = relationship("Chat_Message", backref="subscriptions", uselist=False)
    items = [k for k in locals().keys() if not k.startswith('_')]  # для перебора переменных класса
#     dl = relationship('DriverLicense', backref='person', uselist=False)


# Таблица сообщения в подписках
class Chat_Message(Base):
    __tablename__ = 'chat_messages'
    uid = Column(Integer(), nullable=True)
    id = Column(Integer(), primary_key=True, unique=True)  #  : 289681
    author = Column(String(40))  # {id: "493f786e-0368-4aaa-aac4-abddcbd7df0f"}
    chatId = Column(Integer(), primary_key=True)  # : 145221
    is_content = Column(Boolean())  # : true
    elements = Column(String(40))  # [] # не знаю что это - видимо надо ещё таблицу
    messageUuid = Column(String(40))  # "6bc1dfa5-1785-474a-b5ef-4221808ac5e9"
    read = Column(Boolean())  # : true
    time = Column(DateTime())  # : "2022-06-17T16:55:12.366"
    type = Column(String(20))  #: "MESSAGE"
    value = Column(String(500))  # Тут текст сообщения
    chatRoomId = Column(String(40), ForeignKey('subscriptions.chatRoomId'))
    last_checked_time = Column(DateTime(), nullable=True)
    contentItem = relationship("Content", backref="chat_messages")  # Cвязь с таблицей contentItem
    items = [k for k in locals().keys() if not k.startswith('_')]
# Таблица вложений contentItem


class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer(), primary_key=True, unique=True)  #: 45292
    fileName = Column(String(50))  #: "ДКП гаража 10.docx"
    fileType = Column(String(100))  #: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    fileSize = Column(Integer(), unique=False)  #: 30875
    link = Column(String(150))  #: "MzA4NzU=NDUyOTI=YTI4ZTNiMzktMDNhOC00ZjFkLWJlODgtNGIzZjNhOTIyNTIyMzYwOTkzYTUtNjlkZS00Yjc3LTkzMzgtYjYyNGEzN2QyOWM5"
    status = Column(String(20))  #: "success"
    type = Column(String(20))  #: "application"
    file = Column(LargeBinary)
    messageUuid = Column(String(40), ForeignKey('chat_messages.messageUuid'))
    items = [k for k in locals().keys() if not k.startswith('_')]  # для перебора пременных класса