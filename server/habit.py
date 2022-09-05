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


@app.route("/", methods=["GET", "POST"])
def habit():
    """
    Habits
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


# FIXME: Probably need to merge this with log_habit
@app.route("/log/<habit_id>")
def log(habit_id):
    """
    Get log of habit in JSON form
    """
    habit = Habit.query.filter_by(id=habit_id).first()
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


if __name__ == "__main__":
    db.app.run()
