import os
import pytest
import warnings

from flask_sqlalchemy import SQLAlchemy

from server.model.model import db
from server.habit import create_app, Habit, LoggedHabit

TEST_DB = "/tmp/JUST_A_TEST.db"

UNIT_TEST_SETTINGS = {
    "SQLALCHEMY_DATABASE_URI": f"sqlite:///{TEST_DB}",
    "TEMPLATE_AUTO_RELOAD": True,
    "DEBUG": True,
}

TEST_HABITS = ["veggie meal", "stretches", "cardio exercise"]


@pytest.fixture
def app():
    if os.path.exists(TEST_DB):
        print("Removing old db...")
        os.remove(TEST_DB)
    else:
        print(f"Not there, not removing: {TEST_DB}")

    app = create_app(settings=UNIT_TEST_SETTINGS)

    for habit in TEST_HABITS:
        new_entry = Habit(habitname=habit)
        with app.app_context():
            db.session.add(new_entry)
            db.session.commit()

    return app


# FIXME: Not done yet
def test_delete(app):
    client = app.test_client()
    log = client.get("/")
    print(log)
    _ = client.post("/log/1")
    log = client.get("/habit/1")
    print(log)
    assert len(log.keys()) == 1
