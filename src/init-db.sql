-- PostgreSQL script to initialize all our tables

-- create schema dbo if not exists
CREATE SCHEMA IF NOT EXISTS dbo;

-- create table
CREATE TABLE dbo.user (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(50) NOT NULL,
    bio VARCHAR(250),
    password_hash TEXT NOT NULL,
    role INTEGER NOT NULL DEFAULT 0,
    last_online TIMESTAMP,
    last_post_time TIMESTAMP
);

CREATE TABLE dbo.author (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE dbo.thread (
    id SERIAL PRIMARY KEY,
    doi TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    abstract TEXT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES dbo.author(id)
);

CREATE TABLE dbo.comment (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER NOT NULL REFERENCES dbo.thread(id),
    user_id INTEGER NOT NULL REFERENCES dbo.user(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE dbo.vote (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES dbo.user(id),
    thread_id INTEGER REFERENCES dbo.thread(id),
    comment_id INTEGER REFERENCES dbo.comment(id),
    is_upvote BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE dbo.log (
    id SERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES dbo.user(id),
    description TEXT
);

