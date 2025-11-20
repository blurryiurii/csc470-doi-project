# csc470-doi-project

Project for the CSC470 course. A DOI Lookup &amp; Discussion board for researchers, observers, and 
the curious alike.

## Setup Instructions

1. Go into the source directory

   ```console
   cd src
   ```

2. Start the application using Docker Compose

   ```console
   docker compose up -d
   ```

   This will:
   - Start a PostgreSQL database on port 5432
   - Initialize the database schema automatically
   - Start the Flask web server on port 6767

3. Access the application by opening your browser and navigate to: `http://localhost:6767`

