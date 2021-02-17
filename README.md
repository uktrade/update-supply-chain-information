# defend-data-capture 

A React and DRF app focused on collecting data about the UK's most valuable supply chains. This app is primarily a form in which other government departments can submit updates and provide information about the supply chains they manage. 

## Running the API and its tests

The project uses a `Makefile` to make running commands easier. `make` commands need to be run at the same directory level as the Makefile.

To run the API:
- If you haven't yet created a local database, run `make create-db`
- If you have already created a local db, run `make setup` or `docker-compose up` to bring up the database
- cd into the `/api` folder and run `python manage.py run server`

To add fixture data to the API: 
- If you've followed the instructions above, you can run `make load-data` to load in the fixtures data to the database.

To run API tests:
- Run `make tests`

## Adding Black pre-commit hook

- Generate your pre-commit hooks by running `pre-commit install`.
- When commiting your files, there will be output from Black saying your file has failed, which kickstarts the autocorrector.
- Stage the files again with the Black corrections, and commit.  