from flask import Flask, request, redirect, url_for, session, render_template
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import random
import os
import json

with open("configuration.json") as f:
    CONFIG = json.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['DATABASE_URI']
app.config['SECRET_KEY'] = CONFIG['SECRET_KEY']
db = SQLAlchemy(app)
oauth = OAuth(app)

oauth.register(
    "google",
    client_id=CONFIG['GOOGLE_CLIENT_ID'],
    client_secret=CONFIG['GOOGLE_CLIENT_SECRET'],
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={"scope": "openid email profile"},
)

PROMPTS = CONFIG['PROMPTS']
MAX_WORDS = CONFIG['MAX_WORDS']

class PromptResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    prompt = db.Column(db.String(500), nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    reference_count = db.Column(db.Integer, default=0)
    aggregate_score = db.Column(db.Float, default=0.0)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('prompt_response.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return oauth.google.authorize_redirect(url_for("authorize", _external=True))

@app.route("/authorize")
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    session["user"] = user_info["email"]
    return redirect(url_for("survey"))

@app.route("/survey", methods=["GET", "POST"])
def survey():
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    
    if request.method == "POST":
        selected_prompt = request.form["prompt"]
        response_text = request.form["response"]
        if len(response_text.split()) > MAX_WORDS:
            return "Response too long", 400
        response = PromptResponse(user_email=user_email, prompt=selected_prompt, response=response_text)
        db.session.add(response)
        db.session.commit()
        return redirect(url_for("evaluate"))

    return render_template("survey.html", prompts=PROMPTS)

@app.route("/evaluate", methods=["GET", "POST"])
def evaluate():
    if "user" not in session:
        return redirect(url_for("login"))
    
    user_email = session["user"]
    responses = PromptResponse.query.order_by(db.func.random()).limit(3).all()
    
    if request.method == "POST":
        for response in responses:
            rating = int(request.form.get(f"rating_{response.id}", 0))
            evaluation = Evaluation(user_email=user_email, response_id=response.id, rating=rating)
            db.session.add(evaluation)
            response.reference_count += 1
            db.session.commit()
        return redirect(url_for("index"))
    
    return render_template("evaluate.html", responses=responses)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0",port=8000)

