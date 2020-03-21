# crimson

## Set up a local server
Note: these instructions work for MacOS and should be similar for linux. If you're on windows I pity you.
1. Set up a virtualenv
   ```
   virtualenv -p python3.8 venv
   source venv/bin/activate
   ```
1. Install dependencies
   ```
   pip install -r requirements.txt
   ```
1. Start a local postgres db
   ```
   pg_ctl -D /usr/local/var/postgres start && brew services start postgresql
   ```
1. Check the local db user
   ```
   psql
   # \du
   ```
   Note the configured user and set it as the environment variable `POSTGRES_USER`
   ```
   $ export POSTGRES_USER=[user]
   ```
   Set the user's password under `POSTGRES_PW` if it's anything other than a null password.
1. Setup the local db
   ```
   flask db init
   flask db migrate -m "Initial db migrate"
   flask db upgrade
   flask seed_db
   ```
1. Start the server
   ```
   flask run
   ```
1. Navigate to the server at 127.0.0.1:5000
