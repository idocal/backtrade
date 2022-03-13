# Backtrade

A system for training and backtesting RL algorithms on financial assets.

## Prerequisites
* Node >= 17.3.0
* Python >= 3.8.1
* pip >= 22.0.3

## Installation
Backend (using virtual env):
```sh
$ pip install uvicorn
$ python -m venv vnev
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
```

Frontend:
```sh
$ cd client
$ npm install
```

## How to use
1. Run the API server:
```sh
$ uvicorn api:app --reload --host 0.0.0.0
```
This will load a web server with hot reload on http://localhost:8000

2. Run client server:
```
$ cd client
$ npm run start
```
The website will be loaded on http://localhost:3000
