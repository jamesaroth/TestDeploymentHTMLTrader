from flask import Flask, session

app = Flask(__name__)
app.secret_key = "Please Work"
from flask_app import routes