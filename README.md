# defend-data-capture 

A Django app focused on collecting data about the UK's most valuable supply chains. This app is primarily a form in which other government departments can submit updates and provide information about the supply chains they manage. 

The app uses the standard Django MVC architecture, alongside some Django REST framework end-points. These end-points will allow for the future development of a pipeline that will feed the app's data into [Data Workspace](https://data.trade.gov.uk/). This data will later serve a series of visualisations which will be hosted on Data Workspace.

## Running the app and its tests

The project uses a `Makefile` to make running commands easier. `make` commands need to be run at the same directory level as the Makefile.

To run the app:
- Create a virtual environment using `python3 -m venv env`, and activate it using `source env/bin/activate`
- Run `pip install -r requirements.txt` to install the dependencies into your environment
- If you haven't yet created a local database, run `make create-db`
- If you have already created a local db, run `make setup` or `docker-compose up` to bring up the database
- cd into the `/defend_data_capture` folder and run `python manage.py run server`

To add fixture data: 
- If you've followed the instructions above, you can run `make load-data` to load in the fixtures data to the database.

To run tests:
- Run `make tests`

## Adding Black pre-commit hook

- Generate your pre-commit hooks by running `pre-commit install`.
- When commiting your files, there will be output from Black saying your file has failed, which kickstarts the autocorrector.
- Stage the files again with the Black corrections, and commit.  

## Integrations

### Staff SSO
This project uses DIT's Staff SSO as it's authentication broker, which the app communicates with via [The Django Staff SSO client](https://github.com/uktrade/django-staff-sso-client). This provides a global session around DIT's projects, meaning they all share a centralised authentication. In this app, we extend the authentication slightly, in order to obtain and record the government department that a user should be assigned to. This is done using the domain from the email address in their Staff SSO profile. 

