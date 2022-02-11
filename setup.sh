#!/usr/bin/env bash

# Sets up your local environment to work for this poetry project

declare install

if [ "$1" == "install" ] ; then
    install=true
else
    install=false
fi

if ! command -v poetry > /dev/null 2>&1 ; then
    if $install; then
       	curl -sSL https://install.python-poetry.org | python3
    else
        cat <<- HEREDOC
		Poetry is required to install package dependencies
		Run:
		curl -sSL https://install.python-poetry.org | python3
		HEREDOC
		return 1
    fi
else
	echo "Poetry installed, creating virtual environment and installing packages"
fi

POETRY_VIRTUALENVS_INPROJECT=true poetry install --without dev --sync

if .venv/bin/python3 project_tldr.py --help > /dev/null 2>&1; then
	echo "Poetry installed and Project is ready to run"
	echo "Remember to run 'source .venv/bin/activate' "
	echo "Then execute ./project_tldr.py"
fi