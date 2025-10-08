# csc470-doi-project

Project for the CSC470 course. A DOI Lookup &amp; Discussion board for researchers, observers, and the curious alike.

## Setup instructions (for linux)

1. Create a virtual environment called `env` and activate it

   ```console
   python3 -m venv env
   source env/bin/activate
   ```

2. Pip install `requirements.txt`

   ```console
   pip install -r requirements.txt
   ```

3. Start db docker container

   ```console 
   cd db
   sudo docker compose up -d
   ```

4. Run script to create schema

   ```console
   cd ..

   # You may need to install postgresql package with your package manager
   psql -h localhost -p 5432 -U example -d default_database -f db/init-db.sql
   ```

5. Should be up and working! Run by running:

   ```console
   python proof_of_concept.py
   ```
