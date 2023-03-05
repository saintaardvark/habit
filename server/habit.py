from dataclasses import dataclass
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# from classes import Habit

APP_SETTINGS = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///habits.db",
    "TEMPLATE_AUTO_RELOAD": True,
    "DEBUG": True,
}

TEST_HABITS = ["veggie meal", "stretches", "cardio exercise"]


def create_app(settings=APP_SETTINGS):
    """
    Factory pattern for app making
    """
    app = Flask(__name__)

    # TODO: This is not the recommended way of doing things; see:
    # https://flask.palletsprojects.com/en/2.2.x/config/
    # https://flask.palletsprojects.com/en/2.2.x/api/#flask.Config.from_object
    for k, v in settings.items():
        app.config[k] = v
    return app


def create_db(app):
    """
    Factory pattern for db making
    """
    db = SQLAlchemy(app)
    db.create_all()
    return db

app = create_app()
db = create_db(app)


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
        try:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
        except AttributeError:
            return value

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
    log_time: datetime = db.Column(TimeStamp, default=datetime.utcnow)


# FIXME: These streak calculations should be broken out to another file; need to figure out
# imports for that.
def get_logs_for_habit(habit_id):
    """
    Given a habit ID, return a list of times it was logged.
    Returns:
    - list of ordinals for dates...
    - ...sorted in reverse order.
    """
    log = (
        db.session.query(
            LoggedHabit.log_time.label("log_time"),
        )
        .where(Habit.id == habit_id)
        .where(Habit.id == LoggedHabit.habit_id)
        .group_by(db.func.strftime("%Y-%m-%d", LoggedHabit.log_time))
        .order_by(LoggedHabit.log_time.desc())
        .all()
    )
    list_of_dates = list(set([logtime[0].toordinal() for logtime in log]))
    list_of_dates.sort()
    list_of_dates.reverse()
    return list_of_dates


def calculate_current_streaks(habits):
    """
    Return a count of how many days each habit has been done without interruption.
    """
    habit_logs = {}
    for habit in habits:
        habit_logs[habit.id] = get_logs_for_habit(habit.id)

    return get_streaks_for_habits(habit_logs)


def get_streaks_for_habits(habit_logs):
    """
    Given a list of logs, return the streak for each one.
    """
    streaks = {}

    for habit in habit_logs.keys():
        streak_count = 0
        list_of_dates = get_logs_for_habit(habit)
        streak_count = get_streak_for_single_habit(list_of_dates)
        streaks[habit] = streak_count

    return streaks


def get_streak_for_single_habit(list_of_dates, today=datetime.now().toordinal()):
    """
    Calculate the streak for a single habit.
    """
    # Sad case
    streak_count = 0
    if len(list_of_dates) == 0:
        app.logger.debug("Zero length list_of_dates, streak 0")
        return 0

    latest_date = list_of_dates[0]

    if today - latest_date > 1:
        # The streak ended more than 1 day ago.  Return 0, as you have no chance to make it up.
        return 0

    streak_count = 1
    previous_date = list_of_dates[0]
    for i in range(1, len(list_of_dates)):
        if previous_date - list_of_dates[i] == 1:
            streak_count += 1
            previous_date = list_of_dates[i]
        else:
            break

    app.logger.debug(f"{streak_count=}")

    return streak_count


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
    streaks = calculate_current_streaks(habits)
    return render_template(
        "habits.html", habits=habits, local_timezone=LOCAL_TIMEZONE, streaks=streaks
    )


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
        "calendar.html",
        log=log,
        habit_id=habit_id,
        habitname=habit.habitname,
        local_timezone=LOCAL_TIMEZONE,
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
        LoggedHabit.query.filter_by(habit_id=habit_id).delete()
        db.session.commit()
        return {}


if __name__ == "__main__":
    db.app.run()
