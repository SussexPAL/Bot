# Bot

Project for developing a PAL bot

## Setup

- Firstly make sure you have `pipenv` installed, with the correct version of python (see `Pipfile` for the version)
- Then navigate to this directory in your command line of choice, and then execute `pipenv install`
- Once that's finished, make a copy of the `auth.ini.example` file and name it `auth.ini`
- Then replace `token` value with your discord bot's secret token

## Running The Bot

- To run the bot, firstly navigate to this directory in your command line of choice, and then run `pipenv shell`
  - This will open up a new CLI inside the virtual environment for this project
- Then to run the bot, use `python PAL.py`
