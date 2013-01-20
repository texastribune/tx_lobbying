# tx_lobbying


Very early alpha

## About the data

The two main sources of data are the lists of registered lobbyists, by year:

    <http://www.ethics.state.tx.us/dfs/loblists.htm>

And the coversheets for the lobbyist activies reports (LA):

    <http://www.ethics.state.tx.us/dfs/search_LOBBY.html>

Names come from both sources of data, but only the coversheets have detailed
information about names.

The information for lobbying interests come from the registration forms. This
information is all entered by hand and will be very hard to use without
scrubbing. There should be a way to de-duplicate lobbying interests, and a way
to regenerate a lobbyist's interests based on the raw registration data stored.

The forms can, and are, amended often. When you do updates, it's a good idea
to go back a few years.


## Running tests

Uses nose to run tests, and a separate test only app outside of tx_lobbying.
The test runner is configured to suppress stdout.

    make test

## Development

    pip install -r requirement-dev.txt
