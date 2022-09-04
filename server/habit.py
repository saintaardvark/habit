from flask import Flask, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# from classes import Habit

app = Flask(__name__)
db = SQLAlchemy(app)
db.create_all()


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
app.config["TEMPLATE_AUTO_RELOAD"] = True


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habitname = db.Column(db.String(80), unique=True, nullable=False)


class LoggedHabit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("Habit.id"))
    log_time = db.Column(db.DateTime)


TEST_HABITS = ["veggie meal", "stretches", "cardio exercise"]

# TODO: Only needed the once...
# for habit in TEST_HABITS:
#     new_entry = Habit(habitname=habit)
#     db.session.add(new_entry)
#     db.session.commit()


@app.route("/")
def hello_world():
    """
    Main function
    """
    return "<p>Hello, world!</p>"


@app.route("/habit", methods=["GET", "POST"])
def get_habit():
    """
    Habits
    """
    if request.method == "POST":
        habit = request.form["habit"]
        TEST_HABITS.append(habit)
        new_entry = Habit(habitname=habit)
        db.session.add(new_entry)
        db.session.commit()

    habits = Habit.query.all()
    return render_template("habits.html", habits=habits)


if __name__ == "__main__":
    db.app.run()
