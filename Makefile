include Makefile.venv

serve: venv
	echo "WARNING: You really don't want to do this in prod!"
	cd server && \
		FLASK_APP=habit ../$(VENV)/flask --debug run --host=0.0.0.0

db:
	sqlite3 server/habits.db

# FIXME: Put this in pytest.ini or some such
test:
	pytest --disable-warnings
