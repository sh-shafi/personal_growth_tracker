from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from utils import get_visuals, get_results

app = Flask(__name__)
app.secret_key = "super_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --------------------------------- * Models * --------------------------------- #

# User Model

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    progress_topics = db.relationship('ProgressTopic', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __init__(self, given_name, given_username):
        self.name = given_name
        self.username = given_username

# Progress Topic Model

class ProgressTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    title = db.Column(db.String, nullable=False)  
    needs_to_increase = db.Column(db.Boolean, nullable=False)  
    unit = db.Column(db.String, nullable=False)  
    progress = db.Column(MutableList.as_mutable(db.JSON)) 

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def updateProgress(self, data):
        self.progress = data

    def __init__(self, title, needs_to_increase, unit, user_id):
        self.title = title
        self.needs_to_increase = needs_to_increase
        self.unit = unit
        self.user_id = user_id
        self.progress = []
        

# --------------------------------- * Routes * --------------------------------- #

# Home route with Login and Registration form

@app.route("/") 
def home():
    print(session)
    if "userid" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# Login Handler

@app.route("/login", methods=["POST"]) 
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            session["userid"] = user.id
            return jsonify({"err": 0})
        else:
            return jsonify({"err": 3, "message": "Incorrect Password"})
    else:
        return jsonify({"err": 2, "message": "User does not exist!"})


# Registration Handler
    
@app.route("/register", methods=["POST"]) 
def register():
    data = request.get_json()
    name = data["name"]
    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"err": 1, "message": "User already exists!"})
    else:
        new_user = User(name, username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["userid"] = new_user.id
        return jsonify({"err": 0})


# Dashboard Page        

@app.route("/dashboard") 
def dashboard():
    if "userid" in session:
        user = User.query.filter_by(id=session["userid"]).first()
        if user:
            topics = user.progress_topics
            return render_template("dashboard.html", user=user, topics=topics, length=len(topics))
    return redirect(url_for("home"))


# New Topic Page

@app.route("/new") 
def new_topic():
    if "userid" in session:
        user = User.query.filter_by(id=session["userid"]).first()
        if user:
            return render_template("add.html", user=user)
    return redirect(url_for("home"))


# Specific topic Page

@app.route("/topic/<topicid>") 
def topicPage(topicid):
    if "userid" in session:
        user = User.query.filter_by(id=session["userid"]).first()
        if user:
            id = int(topicid)
            topic = ProgressTopic.query.filter_by(id=id).first()

            print(topic.progress)
 
            if len(topic.progress) == 0:
                return render_template("topic.html", user=user, topic=topic, svg_code="No data to show!", results={})

            svg_code = get_visuals(topic.progress, topic.title, topic.unit)
            results = get_results(topic.progress, topic.needs_to_increase)
            return render_template("topic.html", user=user, topic=topic, svg_code=svg_code, results=results)
    return redirect(url_for("home"))


# Creating new Topic

@app.route("/create", methods=["POST"]) 
def creat_topic():
    if "userid" in session:
        user = User.query.filter_by(id=session["userid"]).first()
        if user:
            data = request.get_json()
            title = data["title"]
            needs_to_increase = data["needs_to_increase"]
            unit = data["unit"]
            user_id = session["userid"]
            topic = ProgressTopic(title, needs_to_increase, unit, user_id)


            db.session.add(topic)
            db.session.commit()

            return jsonify({"err": 0, "message": topic.id})
    return redirect(url_for("home"))


# Adding value to a Topic

@app.route("/topic/<topicid>/add", methods=["POST"]) 
def addvalue(topicid):
    if "userid" in session:
        user = User.query.filter_by(id=session["userid"]).first()
        if user:
            id = int(topicid)
            data = request.get_json()["value"]
            topic = ProgressTopic.query.filter_by(id=id).first()

            progress_list = topic.progress
            progress_list.append(data)  
            topic.progress = progress_list
            
            db.session.commit()

            print(topic.progress)

            return jsonify({"err": 0})
    return redirect(url_for("home"))


# Logout handler

@app.route("/logout") 
def logout():
    session.pop("userid", None)
    return redirect(url_for("home"))


# --------------------------------- * Starting the App * --------------------------------- #

if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)