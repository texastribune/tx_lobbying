# tx_lobbying


Very early alpha

## About the data

The two main sources of data are:

1. The lists of registered lobbyists, by year:
   http://www.ethics.state.tx.us/dfs/loblists.htm

2. And the coversheets for the lobbyist activies reports (LA):
   http://www.ethics.state.tx.us/dfs/search_LOBBY.html

Names come from both sources of data, but only the coversheets have detailed
information about names.

The information for lobbying interests come from the registration forms. This
information is all entered by hand and will be very hard to use without
scrubbing. There should be a way to de-duplicate lobbying interests, and a way
to regenerate a lobbyist's interests based on the raw registration data stored.

The forms can, and are, amended often. When you do updates, it's a good idea
to go back a few years.


## Getting up and running

Set your environment variables. One way is to have a `.env` file with:

```
export DJANGO_SETTINGS_MODULE=example_project.settings
export DATABASE_URL=postgres:///tx_lobbying
```

and then using autoenv or `source .env` to activate it.

Get your database up and running with (Postgres instructions):

    createdb tx_lobbying
    python example_project/manage.py migrate

Then load data with:

    make scrape


## Running tests

    make test

## Development

    pip install -r requirement-dev.txt

The project is configured to use sqlite by default, but if don't want to stab
yourself, set your DATABASE_URL to real database like Postgres.
