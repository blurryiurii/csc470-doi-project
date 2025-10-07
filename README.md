# csc470-doi-project
Project for the CSC470 course. A DOI Lookup &amp; Discussion board for researchers, observers, and the curious alike.

## Setup instructions (for linux)
1. Create a virtual environment called `env`
  - `python3 -m venv env`
2. Pip install `requirements.txt`
  - `pip install -r requirements.txt`
3. Start db docker container
  - `cd db`
  - `sudo docker compose up -d`
4. Run script to create schema
  - `cd ..`
  - `psql -h localhost -p 5432 -U example -d default_database -f db/init-db.sql` (may need to install postgresql package with your package manager)
5. Should be up and working! Run `./proof_of_concept.py` or `python proof_of_concept.py` if the first doesn't work.
