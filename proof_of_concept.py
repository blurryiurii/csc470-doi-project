import requests
import json
import asyncio
import asyncpg

def check_doi(doi):
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    return r.status_code == 200

print("enter 'exit' to quit")

async def create_user(username,password):
    conn = await asyncpg.connect(user='example', password='passw0rd',
                                database='default_database', host='127.0.0.1', port=5432)

    await conn.execute(
        f"insert into dbo.user (account_name, bio, password_hash, role, last_online, last_post_time) values ('{username}', 'bio', '{password}', 1, NOW(), NOW())"
    )
    await conn.close()
async def create_thread(doi,title,abstract,author):
    conn = await asyncpg.connect(user='example', password='passw0rd',
                                database='default_database', host='127.0.0.1', port=5432)

    x=await conn.fetchrow(
        f"SELECT * FROM dbo.author where name = '{author}'"
    )

    if not x:
        await conn.execute("insert into dbo.author (name,email) values ($1,'na')",author
    )


    x = await conn.fetch(
        f"SELECT id FROM dbo.author where name = '{author}'"
    )
    x=x[0]['id']



    await conn.execute(
        "insert into dbo.thread (doi, created_at, abstract, title,author_id) values ($1, NOW(), $2, $3,$4)",doi,abstract,title,x
    )
    await conn.close()

async def check_author(author_name):
    conn = await asyncpg.connect(user='example', password='passw0rd',
                                database='default_database', host='127.0.0.1', port=5432)

    data = await conn.fetchrow(
        f"SELECT * FROM dbo.author where name = '{author_name}'"
    )
    await conn.close()
    return data


async def check_user(username):
    conn = await asyncpg.connect(user='example', password='passw0rd',
                                database='default_database', host='127.0.0.1', port=5432)

    data = await conn.fetchrow(
        f"SELECT * FROM dbo.user  where account_name = '{username}'"
    )
    await conn.close()
    return data
async def check_thread(doi):
    conn = await asyncpg.connect(user='example', password='passw0rd',
                                database='default_database', host='127.0.0.1', port=5432)

    data = await conn.fetchrow(
        f"SELECT * FROM dbo.thread where doi = '{doi}'"
    )
    await conn.close()
    return data




using = True

users = set()

threads = dict()

while using:
    user_name=input("Enter username: ")

    user_exists = asyncio.run(check_user(user_name))

    if not user_exists:
        print("Welcome!")
        password_1 = "___"
        password_2 = ""
        while password_1!=password_2:
            password_1 = input("Enter password: ")
            password_2 = input("Enter password again: ")
            if password_1!=password_2:
                print("Passwords do not match")
        asyncio.run(create_user(user_name,password_1))
    else:
        print(f"Welcome back {user_name}!")
    if user_name=="exit":
        break;
    if user_name in users:
        print(f"Welcome back {user_name}")
    users.add(user_name)

    logged_in = True

    while True:
        #try 10.1002/jcd.21375
        chat = input("Enter DOI (form: 10.####/data): ")
        if chat=="exit":
            break
        if check_doi(chat):
            if asyncio.run(check_thread(chat)):
                print("entered into",chat,"chat")
            else:
                print("Chat created for",chat)
                r = requests.get(f"https://api.crossref.org/works/{chat}")
                data = r.json()
                title = (data["message"]["title"])[0]
                abstract = (data["message"]["abstract"])[0]
                author = (data["message"]["author"][0])["given"] + " " + (data["message"]["author"][0])["family"]
                print(chat,title,abstract)
                asyncio.run(create_thread(chat,title,abstract,author))
            user_input = input()
            while user_input!="exit":
                threads[chat]+=f"\n{user_name}: {user_input}"
                user_input = input()
            if user_input=="exit":
                print(f"Thank you for visiting {chat}!")
        else:
            print("invalid DOI or DOI not found")







