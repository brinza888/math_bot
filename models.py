# -*- coding: utf-8 -*-

# Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from datetime import datetime
from functools import wraps

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

from config import Config


engine = create_engine(Config.DATABASE_URI)

Base = declarative_base()
session_factory = sessionmaker(engine)
Session = scoped_session(session_factory)


class User (Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    last_name = Column(String(64))
    first_name = Column(String(64))
    username = Column(String(32))

    @classmethod
    def new(cls, user_id: int):
        return cls(id=user_id)

    @classmethod
    def get_or_create(cls, db: Session, user_id: int, last_name: str, first_name: str, username: str):
        user = db.query(cls).get(user_id)
        if not user:
            user = User.new(user_id)
            db.add(user)
        user.last_name = last_name
        user.first_name = first_name
        user.username = username
        db.commit()
        return user


class LogRecord (Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User, backref=backref("requests", lazy="dynamic"), uselist=False)

    in_chat_id = Column(Integer)

    command = Column(String(128))
    timestamp = Column(DateTime, default=datetime.now)
    info = Column(Text, default="{}")

    def __init__(self, *args, **kwargs):
        super(LogRecord, self).__init__(*args, **kwargs)

    @classmethod
    def new(cls, user: "User", command: str, chat_id: int, info: dict):
        return cls(
            user_id=user.id,
            command=command,
            info=json.dumps(info, default=lambda obj: str(obj)),
            in_chat_id=chat_id,
        )


class ReportRecord (Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"))

    text = Column(Text, default="{}")
    timestamp = Column(DateTime, default=datetime.now)
    status = Column(String(32))
    link = Column(String(128))

    def __init__(self, *args, **kwargs):
        super(ReportRecord, self).__init__(*args, **kwargs)

    @classmethod
    def new(cls, user: "User", text: str):
        return cls(
            user_id=user.id,
            text=text,
            status="NEW",
            link=None,
        )

    @classmethod
    def get_reports(cls, db: Session, status: str) -> list:
        reports = db.query(cls).filter(ReportRecord.status.like(status.split("_")[2])).all()
        return reports

    @classmethod
    def get_report_by_id(cls, db: Session, id: int):
        return db.query(cls).get(id)

    @classmethod
    def change_status(cls, db: Session, id: int, command: str, link=""):
        report = db.query(cls).get(id)
        if command == "accept_report":
            report.status = "ACCEPTED"
            report.link = link
        if command == "reject_report":
            report.status = "REJECTED"
        if command == "close_report":
            report.status = "CLOSED"
        db.commit()


def get_db():
    session = Session()
    return session


def close_db():
    Session.remove()


def db_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        res = func(*args, **kwargs, db=session)
        Session.remove()
        return res
    return wrapper


def create_all():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_all()
