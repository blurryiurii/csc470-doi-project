# Set-up on a VM (such as GCP)
Free tier: spin up an E2-micro instance

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

Persistence is achieved by binding a docker volume to our db directory where your database changes are reflected.

# Connecting your GUI explorer to PostgreSQL
- I did this through a GUI explorer pgAdmin4
- Linux (Fedora, Debian, Arch...): install with `flatpak install org.pgadmin.pgadmin4`
- Linux: run with `flatpak run org.pgadmin.pgadmin4`, or find the app in your DE applications
- In the Object Explorer, right click on `Servers` > Register > Server
- Name it something distinguishable
- Connection tab: hostname is `localhost`, port 5432, add credentials from the server
- SSH tunneling tab: We'll be using SSH to connect, only port open on VM is 22.
- Use the public IP of the VM, port 22, my email's username, and load the private ssh key into authentication. 

# Connecting to the VM directly
Add an ssh key on your machine and import it into GCP's VM
On linux: `ssh-keygen -t ed25519 -C "youremail@example.com"`
- Walk through the instructions
We'll need to add the public key to the GCP VM.