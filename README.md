# Backtrade

A system for training and backtesting RL algorithms on financial assets.

## Prerequisites
* Node >= 17.3.0
* Python >= 3.8.1
* pip >= 22.0.3

## Installation

### Backend
```sh
$ pip install --upgrade pip
$ pip install uvicorn
$ python -m venv vnev
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
```

### Databases

**MacOS**:
```sh
$ brew update
$ brew install redis postgres
$ psql postgres
postgres-# CREATE ROLE postgres WITH LOGIN PASSWORD 'postgres'
```

Postgres username, password and name should be `postgres`.
Hostname: `localhost`, Port: `5432`

### Frontend
```sh
$ cd client
$ npm install
```

## How to use
1. Start the Postgres server.

**MacOS**:
```sh
$ brew services start poostgresql
$ brew services start redis
```
1b. Initialize the DB structure using **alembic** [OPTIONAL Only when changing DB models and testing]

If running for the first time do inside the api folder
```sh 
$ alembic init alembic
```
Next,

    a. If necessary(when changing models) drop the current tables in the DB by manual cascade drop (can be done in pgAdmin).
        This is only for testing phases.

    b. Run the init revision for alembic. This is the init file which is found in the api/alembic/versions folder. 
        If it doesn't exist run 'alembic revision -m "init" '

```sh
$ alembic upgrade <init revision number>
```
```python
The init revision file should contain the following: 

from api.db.models import Agent, Trade, Balance
def upgrade():
    cols = [c for c in Agent.__table__.columns]
    op.create_table(Agent.__tablename__, *cols)

    cols = [c for c in Balance.__table__.columns]
    op.create_table(Balance.__tablename__, *cols)

    cols = [c for c in Trade.__table__.columns]
    op.create_table(Trade.__tablename__, *cols)
```
    

2. Run the API server:  
```sh
$ export PYTHONPATH="${PYTHONPATH}:${PWD}"
$ cd api
$ uvicorn app:app --reload --host 0.0.0.0
$ redis-cli monitor
$ celery -A worker.app worker --loglevel=info --pool=solo
```

This will load a web server with hot reload on http://localhost:8000

Swagger API is available at: http://localhost:8000/docs

3. Run client server:
```
$ cd client
$ npm run start
```

The website will be loaded on http://localhost:3000
