import sys
import os

# add path to search pac2 module
from app.worker import start_dropbox_worker
from app import create_app
from app.services.auth_service import get_user_by_id
from flask import Flask


app: Flask = create_app()

@app.login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

if __name__ == "__main__":
    start_dropbox_worker(app)
    app.run(host="0.0.0.0", port=9999)
