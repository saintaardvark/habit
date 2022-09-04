serve: venv
	cd server && \
		FLASK_APP=habit flask --debug run

include Makefile.venv
