from dataclasses import dataclass
from datetime import datetime

from flask import Flask, jsonify, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# from classes import Habit

app = Flask(__name__)
db = SQLAlchemy(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///habits.db"
app.config["TEMPLATE_AUTO_RELOAD"] = True
app.config["DEBUG"] = True


@dataclass
class Habit(db.Model):

    id: int = db.Column(db.Integer, primary_key=True)
    # TODO: snake case this
    habitname: str = db.Column(db.String(80), unique=True, nullable=False)


# TODO: a better name for this class would be HabitLog
@dataclass
class LoggedHabit(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    habit_id: int = db.Column(db.Integer, db.ForeignKey("habit.id"))
    log_time: datetime  = db.Column(db.DateTime, default=datetime.utcnow)


db.create_all()
TEST_HABITS = ["veggie meal", "stretches", "cardio exercise"]

# TODO: Only needed the once...
# for habit in TEST_HABITS:
#     new_entry = Habit(habitname=habit)
#     db.session.add(new_entry)
#     db.session.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Index page
    """
    if request.method == "POST":
        habit = request.form["habit"]
        new_entry = Habit(habitname=habit)
        db.session.add(new_entry)
        db.session.commit()

    habits = (
        db.session.query(
            Habit.id,
            Habit.habitname,
            db.func.max(LoggedHabit.log_time).label("log_time"),
        )
        .join(LoggedHabit, Habit.id == LoggedHabit.habit_id, isouter=True)
        .group_by(Habit.id)
        .all()
    )

    return render_template("habits.html", habits=habits)


def normalize_habitname(form_entry):
    """Normalize habit name from form entry

    TODO: This is needed because we're cramming the name of the habit
    into the value of the button we use to log that we did a thing.
    Needless to say, this needs improvement.
    """
    return form_entry.strip("Log ")


@app.route("/calendar/<habit_id>")
def calendar(habit_id):
    """
    Show calendar for individual habit
    """
    habit = Habit.query.filter_by(id=habit_id).first()
    log = (
        db.session.query(
            Habit.id.label("id"),
            Habit.habitname.label("habitname"),
            LoggedHabit.log_time.label("log_time"),
        )
        .where(Habit.id == habit.id)
        .where(Habit.id == LoggedHabit.habit_id)
        .all()
    )

    return render_template(
        "calendar.html", log=log, habit_id=habit_id, habitname=habit.habitname
    )


@app.route("/log/<habit_id>", methods=["GET", "POST"])
def log(habit_id):
    """
    GET log of habit in JSON form, or POST to add a log entry
    """
    habit = Habit.query.filter_by(id=habit_id).first()
    if request.method == "POST":
        new_log = LoggedHabit(habit_id=habit_id)
        db.session.add(new_log)
        db.session.commit()
    log = (
        db.session.query(
            db.func.count(Habit.id).label("count"),
            Habit.habitname.label("habitname"),
            LoggedHabit.log_time.label("log_time"),
        )
        .where(Habit.id == habit_id)
        .where(Habit.id == LoggedHabit.habit_id)
        .group_by(db.func.strftime("%Y-%m-%d", LoggedHabit.log_time))
        .all()
    )
    return_data = {x["log_time"].strftime("%s"): x["count"] for x in log}
    return return_data


@app.route("/habit/<habit_id>", methods=["GET", "DELETE"])
def habit(habit_id):
    """
    Return JSON info for habit
    """
    app.logger.debug(habit_id)
    if request.method == "GET":
        habit = Habit.query.filter_by(id=habit_id).first()
        app.logger.debug(habit)
        return jsonify(habit)

    elif request.method == "DELETE":
        Habit.query.filter_by(id=habit_id).delete()
        return {}

if __name__ == "__main__":
    db.app.run()
