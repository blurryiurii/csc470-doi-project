import os
from datetime import datetime

import requests
from flask import Flask, make_response, request, redirect, url_for, render_template
from sqlalchemy import DateTime, ForeignKey, String, create_engine, select, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from markupsafe import Markup

from conn import database, host, password, port, user

import markdown
import bleach

import re

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

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "h1","h2","h3","h4","h5","h6","table","thead","tbody","tr","td","th",
    "span","div","img","pre","code","blockquote","p","br","hr"
]

ALLOWED_ATTRS = {
    "*": ["class", "id", "style"],
    "a": ["href", "title", "rel"],
    "img": ["src", "alt"]
}


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
    role: Mapped[int] = mapped_column(Integer)
    last_online: Mapped[datetime] = mapped_column(DateTime)
    last_post_time: Mapped[datetime] = mapped_column(DateTime)


class Thread(Base):
    __tablename__: str = "thread"
    __table_args__: dict[str, str] = {"schema": "dbo"}
    id: Mapped[int] = mapped_column(primary_key=True)
    doi: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime)
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
    created_at: Mapped[datetime] = mapped_column(DateTime)


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


def change_bio(user_id: int, message: str) -> None:
    with Session(engine) as session:
        user_to_update = session.query(User).filter_by(id=user_id).first()
        if user_to_update is not None:
            user_to_update.bio = message
        session.commit()


def create_author(name: str, email: str) -> None:
    with Session(engine) as session:
        author = Author(name=name, email=email)
        session.add_all([author])
        session.commit()


def check_doi(doi: str) -> bool:
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    return r.status_code == 200

def get_article_title(doi: str) -> str:
    """
    return the title
    """
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    if r.status_code != 200:
        return "No title available"
    
    try:
        res: str = r.json()["message"]["title"][0]
        return res
    except KeyError:
        return "No title available"

def convert_markdown(raw: str) -> Markup:
    md = markdown.markdown(raw, extensions=["fenced_code", "codehilite"])

    md_clean = bleach.clean(md, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
    linked = bleach.linkify(md_clean)
    return Markup(linked)


def get_article_abstract(doi: str) -> str:
    """
    return the abstract
    """
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    if r.status_code != 200:
        return "No abstract available"
    
    try:
        abstract: str = r.json()["message"]["abstract"]
        abstract = re.sub(r'</?jats:[^>]+>', '', abstract)
        return abstract
    except KeyError:
        return "No abstract available"
    

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


def get_bio_by_id(user_id: int) -> str | None:
    data = []
    with Session(engine) as session:
        stmt = select(User).where(User.id.in_([user_id]))
        data = session.scalars(stmt)
        data = list(data)
    if len(data) == 0:
        return None
    else:
        return data[0].bio


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


def get_raw_thread_list() -> list[Thread]:
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
    
def delete_thread(thread_id: int) -> bool:
    try:
        with Session(engine) as session:
            _ = session.query(Comment).filter(Comment.thread_id == thread_id).delete()
            _ = session.query(Thread).filter(Thread.id == thread_id).delete()
            session.commit()
            return True
    except Exception as e:
        print(f"Error deleting thread: {e}")
        return False


def delete_comment(comment_id: int) -> bool:
    try:
        with Session(engine) as session:
            _ = session.query(Comment).filter(Comment.id == comment_id).delete()
            session.commit()
            return True
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return False


def get_user_role(user_id: int) -> int | None:
    with Session(engine) as session:
        stmt = select(User).where(User.id == user_id)
        data = list(session.scalars(stmt))
        if len(data) == 0:
            return None
        return data[0].role


def is_admin(user_id: int) -> bool:
    role = get_user_role(user_id)
    return role == 2


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
    if username is None:
        #user ID in cookie doesn't exist in database
        resp = make_response(redirect(url_for("login")))
        resp.set_cookie("user_id", "", expires=0) #get rid of it
        return resp
    thread_list = get_raw_thread_list()
    return render_template("home.html", username=username, threads=thread_list)


@app.route("/users/<username>")
def userpage(username: str):
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    cur_user = check_user(username)
    if not cur_user:
        return "invalid user :("
    # user id matches page
    bio = get_bio_by_id(cur_user)
    if bio is None:
        bio = ""
    bio_html = convert_markdown(bio)
    if int(user_id) == int(cur_user):
        return render_template("bio_home.html", bio=bio_html)
    return render_template("bio.html", username=username, bio=bio_html)


@app.route("/thread/<path:doi>")
def thread(doi: str):
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    title = ""
    abstract = ""
    thread_id = check_thread(doi)
    if thread_id is None:
        if check_doi(doi):
            title = get_article_title(doi)
            abstract = get_article_abstract(doi)
            create_thread(doi, abstract, title, 1)
            thread_id = check_thread(doi)
        else:
            return render_template("error.html", message=f"DOI {doi} does not exist")

    if thread_id is not None:
        with Session(engine) as session:
            thread_obj = session.get(Thread, thread_id)
            if thread_obj:
                title = thread_obj.title
                abstract = thread_obj.abstract
        
        raw_chat = get_raw_chat(thread_id)
        comments = [(r.id, get_user_by_id(r.user_id), convert_markdown(r.body)) for r in raw_chat]
        
        # Check if current user is admin
        user_is_admin = is_admin(int(user_id))

        return render_template(
            "thread.html", doi=doi, thread_id=thread_id, comments=comments,
            title=title, abstract=abstract, is_admin=user_is_admin
        )
    return render_template("error.html", message="Thread creation failed")


@app.route("/delete-thread/<int:thread_id>", methods=["POST"])
def delete_thread_route(thread_id: int):
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return "Error: Not logged in", 401
    
    # Check if user is admin
    if not is_admin(int(user_id)):
        return "Error: Unauthorized. Admin access required.", 403
    
    if delete_thread(thread_id):
        return redirect(url_for("Homepage"))
    else:
        return render_template("error.html", message="Failed to delete thread")


@app.route("/delete-comment/<int:comment_id>", methods=["POST"])
def delete_comment_route(comment_id: int):
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return "Error: Not logged in", 401
    
    # Check if user is admin
    if not is_admin(int(user_id)):
        return "Error: Unauthorized. Admin access required.", 403
    
    # Get the DOI to redirect back to the thread
    with Session(engine) as session:
        comment_obj = session.get(Comment, comment_id)
        if comment_obj:
            thread_obj = session.get(Thread, comment_obj.thread_id)
            doi = thread_obj.doi if thread_obj else None
            
            if delete_comment(comment_id):
                if doi:
                    return redirect(url_for("thread", doi=doi))
                return redirect(url_for("Homepage"))
    
    return render_template("error.html", message="Failed to delete comment")


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


@app.route("/update_bio", methods=["POST"])
def update_bio():
    user_id_str = request.cookies.get("user_id")
    if user_id_str is None:
        return "Error: Not logged in", 401
    user_id = int(user_id_str)
    message = request.form.get("bio")
    if message is None:
        return "invalid bio", 400
    change_bio(user_id, message)

    username = get_user_by_id(user_id)
    if username is None:
        return "Error: User not found", 404
    return redirect(url_for("userpage", username=username))


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
    if user_id is None:
        return "Error: Failed to create user", 500
    resp.set_cookie("user_id", str(user_id))
    return resp




if __name__ == "__main__":
    print("starting")
    create_author("John Galt", "john.galt@gmail.com")
    app.run(host="0.0.0.0", port=6767, debug=True)