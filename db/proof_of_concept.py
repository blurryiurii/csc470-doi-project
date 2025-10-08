import requests
import json
import asyncio
import asyncpg
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def Homepage():
    return "<p>Wecome to our app!</p>"


import os


from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import Session
from sqlalchemy import select

from conn import *

conn_str = {
    "user": user,
    "password": password,
    "database": database,
    "host": host,
    "port": port
}
engine = create_engine(f"postgresql+psycopg2://{conn_str["user"]}:{conn_str["password"]}@{conn_str["host"]}:{conn_str["port"]}/{conn_str["database"]}")
from datetime import datetime

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

class Base(DeclarativeBase):
    pass
class Author(Base):
    __tablename__ = "author"
    __table_args__ = {'schema': 'dbo'}
    id: Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(50))
    email:Mapped[str] = mapped_column(String(50))


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'schema': 'dbo'}
    id: Mapped[int] = mapped_column(primary_key=True)
    account_name:Mapped[str] = mapped_column(String(50))
    bio:Mapped[str] = mapped_column(String(250))
    password_hash:Mapped[str] = mapped_column(String(250))
    role:Mapped[int] = mapped_column(String(250))
    last_online:Mapped[DateTime] = mapped_column(DateTime)
    last_post_time:Mapped[DateTime] = mapped_column(DateTime)
class Thread(Base):
    __tablename__ = "thread"
    __table_args__ = {'schema': 'dbo'}
    id: Mapped[int] = mapped_column(primary_key=True)
    doi:Mapped[str] = mapped_column(String(50))
    created_at:Mapped[DateTime] = mapped_column(DateTime)
    abstract:Mapped[str] = mapped_column(String(5000))
    title:Mapped[str] = mapped_column(String(50))
    author_id: Mapped[int] = mapped_column(ForeignKey("dbo.author.id"))
    Base.metadata.create_all(engine)

class Comment(Base):
    __tablename__ = "comment"
    __table_args__ = {'schema': 'dbo'}
    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("dbo.thread.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("dbo.user.id"))
    body:Mapped[str] = mapped_column(String(5000))
    created_at:Mapped[DateTime] = mapped_column(DateTime)

def create_user(username,bio,password):
    if check_user(username):
        print("user already exists")
        return
    with Session(engine) as session:
        user = User(account_name = username,bio=bio,password_hash=password,role=1,last_online=datetime.now(),last_post_time=datetime.now())
        session.add_all([user])
        session.commit()
def create_thread(doi,abstract,title,author_id):
    if check_thread(doi):
        print("thread already exists")
        return
    with Session(engine) as session:
        thread = Thread(doi=doi,created_at=datetime.now(),abstract=abstract,title=title,author_id=author_id)
        session.add_all([thread])
        session.commit()
def check_thread(doi):
    data=[]
    with Session(engine) as session:
        stmt = select(Thread).where(Thread.doi.in_([doi]))
        data = session.scalars(stmt)
        data=list(data)
    if len(data)==0:
        return None
    else:
        return data[0].id

def create_comment(thread_id,user_id,body):
    with Session(engine) as session:
        comment = Comment(thread_id=thread_id,user_id=user_id,body=body,created_at=datetime.now())
        session.add_all([comment])
        session.commit()

def create_author(name,email):
    with Session(engine) as session:
        author = Author(name=name,email=email)
        session.add_all([author])
        session.commit()


def check_doi(doi):
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    return r.status_code == 200

def check_user(username):
    data=[]
    with Session(engine) as session:
        stmt = select(User).where(User.account_name.in_([username]))
        data = session.scalars(stmt)
        data=list(data)
    if len(data)==0:
        return None
    else:
        return data[0].id
def get_user_by_id(user_id):
    data=[]
    with Session(engine) as session:
        stmt = select(User).where(User.id.in_([user_id]))
        data = session.scalars(stmt)
        data=list(data)
    if len(data)==0:
        return None
    else:
        return data[0].account_name
 
def check_author(name):
    data=[]
    with Session(engine) as session:
        stmt = select(Author).where(Author.name.in_([name]))
        data = session.scalars(stmt)
        data=list(data)
    if len(data)==0:
        return None
    else:
        return data[0].id

def get_raw_chat(thread_id):
    data=[]
    with Session(engine) as session:
        stmt = select(Comment).where(Comment.thread_id.in_([thread_id])).order_by(Comment.created_at)
        data = session.scalars(stmt)
        data=list(data)
    return data


'''
user_id=check_user("John")
if not user_id:
    create_user("John","I am a CS student","password")
    user_id=check_user("John")
author_id = check_author("Justin Schroeder")
if not author_id:
    create_author("Justin Schroeder","...@...")
    author_id = check_author("Justin Schroeder")
thread_id=check_thread("10.1002/jgt.21783")
if not thread_id:
    create_thread("10.1002/jgt.21783","In ...","Orientable Hamilton Cycle Embeddings of Complete Tripartite Graphs II: Voltage Graph Constructions and Applications",author_id)
    thread_id=check_thread("10.1002/jgt.21783")
print(user_id)
print(thread_id)
print(author_id)

while True:
    if os.name == 'nt':  
        os.system('cls')
    else:  
        os.system('clear')
    thread=get_raw_chat(thread_id)
    for message in thread:
        username =get_user_by_id(message.user_id)
        body = message.body
        print(username,":",body)
    username =get_user_by_id(user_id)
    new_message = input(username+" : ")
    create_comment(thread_id,user_id,new_message)
'''
