from dataclasses import dataclass
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
