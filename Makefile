# create virtual environment
PYTHON = python2.7

.env:
	virtualenv .env -p $(PYTHON)

# install all needed for development
develop: .env
	.env/bin/pip install -e . -r dev_requirements.txt tox

# clean the development envrironment
clean:
	-rm -rf .env
