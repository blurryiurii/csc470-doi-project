# Set-up on a VM (such as GCP)
Free tier: spin up an E2-micro instance
Optional: Add an ssh key on your machine and import it into GCP's VM

Update the machine with `sudo apt update && sudo apt upgrade`
Install Docker:
```
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```
clone the git repo on the VM
change `db-creds.env`
run the docker compose file

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
