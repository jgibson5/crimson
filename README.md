# crimson

## Set up a local server
1. Set up a virtualenv
   ```
      virtualenv -p python3.8 venv
      source venv/bin/activate
   ```
1. Install dependencies
   `pip install -r requirements.txt`
1. Setup the local db
   ```
      flask db init
      flask db migrate -m "Initial db migrate"
      flask db upgrade
      flask seed_db
   ```
1. Start the server
   `flask run`
1. Navigate to the server at 127.0.0.1:5000
