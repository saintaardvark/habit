from flask import Flask, request

from classes import Habit, db

db.create_all()
app = Flask(__name__)

TEST_HABITS = ["veggie meal", "stretches", "cardio exercise"]

for habit in TEST_HABITS:
    new_entry = Habit(habitname=habit)
    db.session.add(new_entry)
    db.session.commit()


@app.route("/")
def hello_world():
    """
    Main function
    """
    return "<p>Hello, world!</p>"


@app.route("/habit")
def get_habit():
    """
    Get habits
    """
    body = "<h1>Habits</h1><div id='habits'><ul>"
    for habit in TEST_HABITS:
        body += f"<li>{habit}</li>"

    body += "</ul>"
    return body


@app.route("/habit/<habit>", methods=["POST"])
def create_habit(habit):
    """
    Create habit
    """
    TEST_HABITS.append(habit)
    return f"Added {habit}"
