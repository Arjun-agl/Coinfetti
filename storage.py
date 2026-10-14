import json
import os

DATA_DIR = "data"
PORTFOLIO_DIR = os.path.join(DATA_DIR, "portfolios")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(PORTFOLIO_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    return load_json(USERS_FILE, {})

def save_users(users):
    save_json(USERS_FILE, users)

def portfolio_path(username):
    return os.path.join(PORTFOLIO_DIR, f"{username}.json")

def load_portfolio(username):
    return load_json(portfolio_path(username), {
        "holdings": {},
        "watchlist": []
    })

def save_portfolio(username, data):
    save_json(portfolio_path(username), data)
