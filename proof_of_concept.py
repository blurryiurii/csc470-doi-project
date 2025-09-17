import requests
import json
import asyncio
import asyncpg

def check_doi(doi):
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    return r.status_code == 200

print("enter 'exit' to quit")

async def run():
    conn = await asyncpg.connect(user='example', password='passw0rd',
                                database='doi', host='127.0.0.1', port=5432)

    await conn.execute(
        "insert into dbo.user (account_name, bio, password_hash, role, last_online, last_post_time) values ('name', 'bio', 'aB2df2e', 1, NOW(), NOW())"
    )
    await conn.close()

asyncio.run(run())

using = True

users = set()

threads = dict()

while using:
    user_name=input("Enter username: ")
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
            if chat in threads:
                print("entered into",chat,"chat")
            else:
                print("Chat created for",chat)
                r = requests.get(f"https://api.crossref.org/works/{chat}")
                data = r.json()
                title = (data["message"]["title"])[0]
                threads[chat]=title
            print(threads[chat])
            user_input = input()
            while user_input!="exit":
                threads[chat]+=f"\n{user_name}: {user_input}"
                user_input = input()
            if user_input=="exit":
                print(f"Thank you for visiting {chat}!")
        else:
            print("invalid DOI or DOI not found")







