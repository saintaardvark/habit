from dataclasses import dataclass
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# from classes import Habit

app = Flask(__name__)
db = SQLAlchemy(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///habits.db"
app.config["TEMPLATE_AUTO_RELOAD"] = True
app.config["DEBUG"] = True

# Note:  We're setting the timezone based on where the serve is running.
# This is *heavily* optimized for my use case, where:
# a) I'm running this on my li'l home server,
# b) its timezone is set to America/Vancouver, and
# c) that matches my own timezone as well.
LOCAL_TIMEZONE = datetime.utcnow().astimezone().tzinfo

# Hat tip to https://mike.depalatis.net/blog/sqlalchemy-timestamps.html
class TimeStamp(db.TypeDecorator):
    impl = db.DateTime
    LOCAL_TIMEZONE = LOCAL_TIMEZONE

    def process_bind_param(self, value: datetime, dialect):
        # Note: returning value untouched, on the assumption that the LoggedHabit takes care of
        # setting the TZ correctly.  If that changes, this is the code that's in the original example:
        # if value.tzinfo is None:
        #     app.logger.debug(f"[process_bind_param] tzinfo: None!  about to set to {self.LOCAL_TIMEZONE}")
        #     value = value.astimezone(self.LOCAL_TIMEZONE)
        # return value.astimezone(timezone.utc)

        # ...but as it is, we'll just leave it alone:
        return value

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

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
    # FIXME: I'm not sure that the timezone=True is working the way I
    # want it to.  See:
    # - https://docs.sqlalchemy.org/en/14/dialects/sqlite.html
    log_time: datetime = db.Column(TimeStamp, default=datetime.utcnow())


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
    # This is *very* optimized for my use case.  For more details, see the
    # comment for LOCAL_TIMEZONE.
    return render_template(
        "calendar.html", log=log, habit_id=habit_id, habitname=habit.habitname, local_timezone=LOCAL_TIMEZONE
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
        db.session.commit()
        return {}

if __name__ == "__main__":
    db.app.run()
