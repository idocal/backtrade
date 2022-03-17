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
```
$ brew services start poostgresql
```
2. Run the API server:  
```sh
$ cd api
$ uvicorn api:app --reload --host 0.0.0.0
$ redis-cli monitor
$ celery -A worker.app worker --logleve=info --pool=solo(needed for windows) (from withing the api folder)
```

This will load a web server with hot reload on http://localhost:8000

Swagger API is available at: http://localhost:8000/docs

3. Run client server:
```
$ cd client
$ npm run start
```

The website will be loaded on http://localhost:3000
