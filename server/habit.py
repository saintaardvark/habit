from datetime import datetime

from flask import Flask, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# from classes import Habit

app = Flask(__name__)
db = SQLAlchemy(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
app.config["TEMPLATE_AUTO_RELOAD"] = True
app.config["DEBUG"] = True

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: snake case this
    habitname = db.Column(db.String(80), unique=True, nullable=False)


# TODO: a better name for this class would be HabitLog
class LoggedHabit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habit.id"))
    log_time = db.Column(db.DateTime, default=datetime.utcnow)


db.create_all()
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
def habit():
    """
    Habits
    """
    if request.method == "POST":
        habit = request.form["habit"]
        new_entry = Habit(habitname=habit)
        db.session.add(new_entry)
        db.session.commit()


    # habits = Habit.query.all()
    # TODO: This is not working yet.
    habits = db.session.query(
        Habit, LoggedHabit
    ).filter(
        Habit.id == LoggedHabit.habit_id
    ).all()
    app.logger.debug(habits)
    return render_template("habits.html", habits=habits)


@app.route("/log_habit", methods=["POST"])
def log_habit():
    """
    Habits
    """
    app.logger.debug(f"Form: {request.form}")
    habitname = request.form["log"].split()[-1]

    habit = Habit.query.filter_by(habitname=habitname).first()
    new_log = LoggedHabit(habit_id=habit.id)
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for("habit"))


if __name__ == "__main__":
    db.app.run()
