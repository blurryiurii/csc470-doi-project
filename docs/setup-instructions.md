# Setup instructions
These instructions worked to set up an instance on a Debian VM on GCP's `e2-micro instance`

1. Update the machine with `sudo apt update && sudo apt upgrade`

2. Install Docker
   ```bash
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

3. Clone this repository
   
   `git clone https://github.com/blurryiurii/csc470-doi-project`

4. Change working directory to `src`

5. Change `db-creds.env` to a better set of credentials.

6. Change `docker-compose.yml` to your liking, especially the database folder location (`db`).
   This achieves persistance of data across server restarts

7. Start the application using Docker Compose: `docker compose up -d`

   This will:
- Start a PostgreSQL database on port 5432
- Initialize the database schema automatically
- Start the Flask web server on port 6767

8. Access the application by navigating to `http://<your_ip>:6767`


# Connecting your GUI explorer to PostgreSQL
- I did this through a GUI explorer pgAdmin4
- Install from here: `https://www.pgadmin.org/download/`
- If you like flatpaks on Linux, install from FlatHub with:
   `flatpak install flathub org.pgadmin.pgadmin4`
   Run with `flatpak run org.pgadmin.pgadmin4`, or find pgadmin in your applications
- In the Object Explorer, right click on `Servers` > Register > Server
- Name it something distinguishable
- Connection tab: hostname is the machine's IP, port 5432, add credentials from the server
- SSH tunneling tab: We'll be using SSH to connect.
- Use the public IP of the VM, port 22, your email, and load the private ssh key into authentication. 

# Connecting to the VM using SSH keys (Linux instructions)
To log into your server using an SSH key, generate a key on your machine and add it to the server.

Generate your SSH key: `ssh-keygen -t ed25519 -C "youremail@example.com"`

Add this key to your server using `ssh-copy-id` ([instructions](https://www.ssh.com/academy/ssh/copy-id))