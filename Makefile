serve: venv
	cd server && \
		FLASK_APP=habit flask run

include Makefile.venv
