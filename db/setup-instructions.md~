# PostgreSQL
- Install [docker](https://docs.docker.com/compose/install/) (official one, with `docker compose` support)
- Ensure the docker daemon is running (`sudo systemctl status docker.service`)
- If it's not, start and enable it on startup (`sudo systemctl enable --now docker.service`)
- Navigate to this directory within the project (`db`)
- Run `sudo docker compose up -d`
- This runs the services defined in docker-compose.yml
- PostgreSQL will now run on port 5432

Persistence is achieved by binding a docker volume to our db directory where your database changes are reflected.

# Connecting your GUI explorer to PostgreSQL
- I did this through a GUI explorer pgAdmin4
- Linux (Fedora, Debian, Arch...): install with `flatpak install org.pgadmin.pgadmin4`
- Linux: run with `flatpak run org.pgadmin.pgadmin4`, or find the app in your DE applications
- In the Object Explorer, right click on `Servers` > Register > Server
- Name it something distinguishable
- Connection tab: hostname is `localhost`, port 5432 if running on your machine

# Initial setup
Use pgAdmin4 to create a database `doi`.

Create a database, add tables with columns in accordance with our [Plan](https://docs.google.com/document/d/1JaCjudOS43ThM-KK7oG8mUY-IwXx-uDua0S-QsC5OSs).
- `user`
- `author`
- `thread`
- `comment`
- `vote`
- `log`

To initialize, run the `init-db.sql` script to initialize the schema and tables.

Now, Postgres should be ready to populate!
