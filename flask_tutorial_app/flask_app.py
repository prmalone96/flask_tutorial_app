from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "app_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=5)

db = SQLAlchemy(app)


class Contacts(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    address = db.Column(db.String(100))
    birthday = db.Column(db.String(100))
    user_id = db.Column(db.Integer)

    def __init__(self, name, email, address, birthday, user_id):
        self.name = name
        self.email = email
        self.address = address
        self.birthday = birthday
        self.user_id = user_id

    @property
    def id(self):
        return self._id


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @property
    def id(self):
        return self._id


@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    if "user_id" in session:
        return render_template("index.html", values=Contacts.query.filter_by(user_id=session["user_id"]))
    else:
        flash("You are not logged in")
        return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        logged_in_user = Users.query.filter_by(
            username=request.form["username"], password=request.form["password"]).first()
        if logged_in_user:
            session["user_id"] = logged_in_user.id
            return redirect("/")
        else:
            flash("You failed to log in, either try again, or create a new user", "info")
    return render_template("login.html")


@app.route("/create_user", methods=["POST", "GET"])
def create_user():
    if request.method == "POST":
        un = request.form["username"]
        existing_user = Users.query.filter_by(username=un).first()
        if existing_user:
            flash("Account for Username Already Exists, Please Try Again")
        else:
            new_user = Users(un, request.form["password"])
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("create_user.html")


@app.route("/edit_contact/<contact_id>", methods=["POST", "GET"])
def edit_contact(contact_id):
    if request.method == "POST":
        email = request.form["email"]
        address = request.form["address"]
        birthday = request.form["birthday"]
        found_user = Contacts.query.filter_by(_id=contact_id).first()
        contact_name = found_user.name
        found_user.email = email
        found_user.address = address
        found_user.birthday = birthday
        db.session.commit()
        flash("Information was saved!")
    else:
        found_user = Contacts.query.filter_by(_id=contact_id).first()
        contact_name = found_user.name
        email = found_user.email
        address = found_user.address
        birthday = found_user.birthday
    return render_template("edit_contact.html", user=contact_name, email=email, address=address, birthday=birthday)


@app.route("/add_contact", methods=["POST", "GET"])
def add_contact():
    return render_template("new_contact.html")


@app.route("/add_contact_helper", methods=["POST"])
def add_contact_helper():
    new_contact_name = request.form["contact_name"]
    new_contact = Contacts(new_contact_name, "", "", None, session["user_id"])
    db.session.add(new_contact)
    db.session.commit()
    contact_id = new_contact.id
    return redirect(f"edit_contact/{contact_id}")


@app.route("/delete/<contact_id>")
def delete_contact(contact_id):
    found_contact = Contacts.query.filter_by(_id=contact_id).first()
    db.session.delete(found_contact)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("user_id", None)
    return redirect("login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
