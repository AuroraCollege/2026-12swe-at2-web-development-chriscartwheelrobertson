from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_database, init_database

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-production"

# Initialise the database
with app.app_context():
    init_database()



# Timeline routes

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")
