import os
from datetime import datetime

import requests
from flask import Flask, make_response, request, redirect, url_for, render_template
from sqlalchemy import DateTime, ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from conn import database, host, password, port, user

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


def get_user_password_by_id(user_id: int) -> str | None:
    data = []
    with Session(engine) as session:
        stmt = select(User).where(User.id.in_([user_id]))
        data = session.scalars(stmt)
        data = list(data)
    if len(data) == 0:
        return None
    else:
        return data[0].password_hash


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
    data = []
    with Session(engine) as session:
        stmt = select(Thread)
        data = session.scalars(stmt)
        data = list(data)
    return data


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


app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "templates"
    ),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
)


@app.route("/")
def Homepage():
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))
    username = get_user_by_id(int(user_id))
    thread_list = get_raw_thread_list()
    return render_template("home.html", username=username, threads=thread_list)


@app.route("/thread/<path:doi>")
def thread(doi: str):
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    thread_id = check_thread(doi)
    if thread_id is None:
        if check_doi(doi):
            create_thread(doi, "who is john galt", "Who is John Galt?", 1)
            thread_id = check_thread(doi)
        else:
            return render_template("error.html", message=f"DOI {doi} does not exist")

    if thread_id is not None:
        raw_chat = get_raw_chat(thread_id)
        comments = [(get_user_by_id(r.user_id), r.body) for r in raw_chat]
        return render_template(
            "thread.html", doi=doi, thread_id=thread_id, comments=comments
        )
    return render_template("error.html", message="Thread creation failed")


@app.route("/send-it", methods=["POST"])
def send_message():
    user_id_str = request.cookies.get("user_id")
    if user_id_str is None:
        return "Error: Not logged in", 401
    user_id = int(user_id_str)
    message = request.form.get("userText")
    thread_id_str = request.form.get("thread_id")
    if message is None or thread_id_str is None:
        return "Error: Missing message or thread_id", 400
    thread_id = int(thread_id_str)
    create_comment(thread_id, user_id, message)
    doi = request.form.get("doi")
    return redirect(url_for("thread", doi=doi))


@app.route("/login")
def login() -> str:
    return render_template("login.html")


@app.route("/sign-in", methods=["POST"])
def sign_in():
    resp = make_response(redirect(url_for("Homepage")))
    username = request.form.get("username")
    password = request.form.get("password")
    if username is None or password is None:
        return "Error: Missing username or password", 400
    user_id = check_user(username)
    if not user_id:
        return redirect(url_for("sign_up"))
    # Security 100
    if password != get_user_password_by_id(user_id):
        return "<p>Ah ah ah! You didn't say the magic word!</p>", 400
    assert user_id
    resp.set_cookie("user_id", str(user_id))

    return resp


@app.route("/go-to-thread", methods=["POST"])
def go_to_thread():
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    doi = request.form.get("doi")
    if doi is None or doi.strip() == "":
        return redirect(url_for("Homepage"))

    doi = doi.strip()

    return redirect(url_for("thread", doi=doi))


@app.route("/sign-up")
def sign_up():
    return render_template("signup.html")


@app.route("/create-account", methods=["POST"])
def create_account():
    resp = make_response(redirect(url_for("Homepage")))
    username = request.form.get("username")
    password = request.form.get("password")
    password_verify = request.form.get("password_verify")
    if username is None or password is None or password_verify is None:
        return "Missing required fields"
    if check_user(username):
        return "user already exists"
    if password != password_verify:
        return "Passwords do not match"
    create_user(username, "i am john galt", password)
    user_id = check_user(username)
    resp.set_cookie("user_id", str(user_id))
    return resp


if __name__ == "__main__":
    print("starting")
    create_author("John Galt", "john.galt@gmail.com")
    app.run(host="0.0.0.0", port=6767, debug=True)
