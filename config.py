from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

import datetime
from base.models import User, Role

database = 'sqlite:///base/sqlite3.db'
ADMIN = 358708312

default_admin = User(
    id=358708312,
    first_name='Александр',
    username=None,
    last_name='Кожевников',
    language_code='en',
    role=0,
    updated=datetime.datetime.now
    )

# Роли для таблицы
a = Role(id=0, role_type='admin')
a1 = Role(id=1, role_type='user')
a2 = Role(id=2, role_type='group_admin')
