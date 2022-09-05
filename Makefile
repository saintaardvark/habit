serve: venv
	echo "WARNING: You really don't want to do this in prod!"
	cd server && \
		FLASK_APP=habit flask --debug run --host=0.0.0.0

include Makefile.venv
