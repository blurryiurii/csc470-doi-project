from datetime import datetime

import requests
from flask import Flask, make_response, request
from sqlalchemy import DateTime, ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

<<<<<<< Updated upstream:src/main.py
from conn import database, host, password, port, user
=======
from flask import make_response
from flask import abort, redirect, url_for

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
>>>>>>> Stashed changes:src/proof_of_concept.py

conn_str = {
    "user": user,
    "password": password,
    "database": database,
    "host": host,
    "port": port,
}
engine = create_engine(
    f"postgresql+psycopg2://{conn_str['user']}:{conn_str['password']}@{conn_str['host']}:{conn_str['port']}/{conn_str['database']}"
)


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__: str = "author"
    __table_args__: dict[str, str] = {"schema": "dbo"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))


class User(Base):
    __tablename__: str = "user"
    __table_args__: dict[str, str] = {"schema": "dbo"}
    id: Mapped[int] = mapped_column(primary_key=True)
    account_name: Mapped[str] = mapped_column(String(50))
    bio: Mapped[str] = mapped_column(String(250))
    password_hash: Mapped[str] = mapped_column(String(250))
    role: Mapped[int] = mapped_column(String(250))
    last_online: Mapped[DateTime] = mapped_column(DateTime)
    last_post_time: Mapped[DateTime] = mapped_column(DateTime)


class Thread(Base):
    __tablename__: str = "thread"
    __table_args__: dict[str, str] = {"schema": "dbo"}
    id: Mapped[int] = mapped_column(primary_key=True)
    doi: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    abstract: Mapped[str] = mapped_column(String(5000))
    title: Mapped[str] = mapped_column(String(50))
    author_id: Mapped[int] = mapped_column(ForeignKey("dbo.author.id"))
    Base.metadata.create_all(engine)


class Comment(Base):
    __tablename__: str = "comment"
    __table_args__: dict[str, str] = {"schema": "dbo"}
    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("dbo.thread.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("dbo.user.id"))
    body: Mapped[str] = mapped_column(String(5000))
    created_at: Mapped[DateTime] = mapped_column(DateTime)


def create_user(username: str, bio: str, password: str) -> None:
    if check_user(username):
        print("user already exists")
        return
    with Session(engine) as session:
        user = User(
            account_name=username,
            bio=bio,
            password_hash=password,
            role=1,
            last_online=datetime.now(),
            last_post_time=datetime.now(),
        )
        session.add_all([user])
        session.commit()


def create_thread(doi: str, abstract: str, title: str, author_id: int) -> None:
    if check_thread(doi):
        print("thread already exists")
        return
    with Session(engine) as session:
        thread = Thread(
            doi=doi,
            created_at=datetime.now(),
            abstract=abstract,
            title=title,
            author_id=author_id,
        )
        session.add_all([thread])
        session.commit()


def create_comment(thread_id: int, user_id: int, body: str) -> None:
    with Session(engine) as session:
        comment = Comment(
            thread_id=thread_id, user_id=user_id, body=body, created_at=datetime.now()
        )
        session.add_all([comment])
        session.commit()


def create_author(name: str, email: str) -> None:
    with Session(engine) as session:
        author = Author(name=name, email=email)
        session.add_all([author])
        session.commit()


def check_doi(doi: str) -> bool:
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    return r.status_code == 200


def check_user(username: str) -> int | None:
    data = []
    with Session(engine) as session:
        stmt = select(User).where(User.account_name.in_([username]))
        data = session.scalars(stmt)
        data = list(data)
    if len(data) == 0:
        return None
    else:
        return data[0].id


def get_user_by_id(user_id: int) -> str | None:
    data = []
    with Session(engine) as session:
        stmt = select(User).where(User.id.in_([user_id]))
        data = session.scalars(stmt)
        data = list(data)
    if len(data) == 0:
        return None
    else:
        return data[0].account_name


def check_author(name: str) -> int | None:
    data = []
    with Session(engine) as session:
        stmt = select(Author).where(Author.name.in_([name]))
        data = session.scalars(stmt)
        data = list(data)
    if len(data) == 0:
        return None
    else:
        return data[0].id


def get_raw_chat(thread_id: int) -> list[Comment]:
    data = []
    with Session(engine) as session:
        stmt = (
            select(Comment)
            .where(Comment.thread_id.in_([thread_id]))
            .order_by(Comment.created_at)
        )
        data = session.scalars(stmt)
        data = list(data)
    return data
def get_raw_thread_list():
    data=[]
    with Session(engine) as session:
        stmt = select(Thread)
        data = session.scalars(stmt)
        data=list(data)
    return data



"""
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
"""


def check_thread(doi: str) -> int | None:
    data = []
    with Session(engine) as session:
        stmt = select(Thread).where(Thread.doi.in_([doi]))
        data = session.scalars(stmt)
        data = list(data)
    if len(data) == 0:
        return None
    else:
        return data[0].id


app = Flask(__name__)


@app.route("/")
<<<<<<< Updated upstream:src/main.py
def Homepage() -> str:
    return "<p>Wecome to our app!!</p>"
=======
def Homepage():
    user_id = (request.cookies.get("user_id"))
    if user_id == None:
        return redirect(url_for('login'))
    ret_str = f"<p>Wecome to our app {get_user_by_id(user_id)}!!</p>"
    ret_str+=f"<p>Available threads: </p><br>"
    ret_str+=f"<p>Navigate to url/thread/doi (with doi= one of the values below) to access thread: </p><br>"
    thread_list = get_raw_thread_list()
    for t in thread_list:
        url=url_for('thread',doi=t.doi)
        ret_str+=f'<a href="{url}">{t.doi}</a><br>'
    return ret_str
>>>>>>> Stashed changes:src/proof_of_concept.py


@app.route("/thread/<path:doi>")
<<<<<<< Updated upstream:src/main.py
def thread(doi: str) -> str:
    print("thread")
=======
def thread(doi):
>>>>>>> Stashed changes:src/proof_of_concept.py
    thread_id = check_thread(doi)
    if thread_id is None:
        x = check_doi(doi)
        if x:
            create_thread(doi, "who is john galt", "Who is John Galt?", 1)
        else:
            return f"<p>DOI {doi} does not exist</p>"
    thread_id = check_thread(doi)
    if thread_id is None:
        return f"<p>Error: Thread {doi} could not be created</p>"
    ret_str = f"<p>thread {doi} {thread_id}</p>\n"
    raw_chat = get_raw_chat(thread_id)
    for r in raw_chat:
        ret_str += "<p>" + str(get_user_by_id(r.user_id)) + ": " + str(r.body) + "</p>"
        ret_str += "<br>"
    form = f'''<form action="/send-it" method="post">
  <label for="message">Enter your text:</label><br>
  <input type="text" id="message" name="userText" required><br><br>
<input type="hidden" name="thread_id" value="{thread_id}">
<input type="hidden" name="doi" value="{doi}">
  <input type="submit" value="Submit">
</form>'''
    ret_str += form
    return ret_str


@app.route("/send-it", methods=["POST"])
def send_message() -> str | tuple[str, int]:
    user_id_str = request.cookies.get("user_id")
    if user_id_str is None:
        return "Error: Not logged in", 401
    user_id = int(user_id_str)
    message = request.form.get("userText")
<<<<<<< Updated upstream:src/main.py
    thread_id_str = request.form.get("thread_id")
    if message is None or thread_id_str is None:
        return "Error: Missing message or thread_id", 400
    thread_id = int(thread_id_str)
    create_comment(thread_id, user_id, message)
    return f"Data received successfully!\n{thread_id}"


=======
    thread_id = request.form.get("thread_id")
    create_comment(thread_id,user_id,message)
    return redirect(url_for('thread',doi=request.form.get("doi")))
>>>>>>> Stashed changes:src/proof_of_concept.py
@app.route("/login")
def login() -> str:
    ret_str = ""
    form = """<form action="/sign-in" method="post">
  <label for="username">Enter your username:</label><br>
  <input type="text" id="username" name="username" required><br><br>
  <label for="password">Enter your password:</label><br>
  <input type="password" id="password" name="password" required><br><br>
  <input type="submit" value="Submit">
</form>"""
    ret_str += form
    return ret_str


@app.route("/sign-in", methods=["POST"])
def log_in():
    resp = make_response("session")
    username = request.form.get("username")
    password = request.form.get("password")
    if username is None or password is None:
        return "Error: Missing username or password", 400
    user_id = check_user(username)
    if not user_id:
        user_id = create_user(username, "Who is john galt?", password)
    resp.set_cookie("user_id", str(user_id))

    return resp


if __name__ == "__main__":
    print("starting")
    create_author("John Galt", "john.galt@gmail.com")
    create_user("John Galt", "i am john galt", "Password1!")
    app.run(host="0.0.0.0", debug=True)
