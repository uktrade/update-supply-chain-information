# update-supply-chain-information

A Django app focused on collecting data about the UK's most valuable supply chains. This app is primarily a form in which other government departments can submit updates and provide information about the supply chains they manage.

The app uses the standard Django MVC architecture, alongside some Django REST framework end-points. These end-points will allow for the future development of a pipeline that will feed the app's data into [Data Workspace](https://data.trade.gov.uk/). This data will later serve a series of visualisations which will be hosted on Data Workspace.

## Running the app and its tests

Python version 3.8 is required to run this project - [install here](https://www.python.org/downloads/release/python-380/).

The project uses a `Makefile` to make running commands easier. `make` commands need to be run at the same directory level as the Makefile.

### Setting up environment variables:
- Environment variables can be found in the `update_supply_chain_information/sample.env`
- Copy these to a `.env` file in the `update_supply_chain_information` folder
- The `AUTHBROKER_CLIENT_ID` and `AUTHBROKER_CLIENT_SECRET` values needed for staff SSO can be found in [passman](https://passman.ci.uktrade.digital/2fa/verify/?next=/secret/61f0a3bf-33f3-427e-8ade-cdee0c637031/)

### Setting up static files
The project uses [webpack](https://webpack.js.org/) to build static files, to setup:
- Install node version 14.x
- Run `npm install` to install all node modules, including webpack and the govuk-frontend npm package
- Run `npm run dev` - webpack will then bundle all static files in `update_supply_chain_information/assets` and create 'bundles' in `update_supply_chain_information/assets/webpack_bundles`. When making changes to static files, e.g. updating `application.scss`, webpack will recompile the files when edited and create a new bundle.

### Styles
The project mainly uses styles from the [govuk-frontend](https://github.com/alphagov/govuk-frontend) npm package. Examples of how to use these styles can be found in components on the [GOVUK design system](https://design-system.service.gov.uk/components/).

Where it is not possible to use a govuk style, the [moj-frontend](https://github.com/ministryofjustice/moj-frontend) library (an extension of govuk-frontend) has been used, and any custom styles added to `update_supply_chain_information/assets/application.scss`, with classes prefixed with `.app-`.

### To run the app:
- Create a virtual environment using `python3 -m venv env`, and activate it using `source env/bin/activate`
- Run `pip install -r requirements.txt` to install the dependencies into your environment
- If you haven't yet created a local database, run `make create-db`. This will create the database, run migrations, create  initial reversions and load fixture data.
- If you have already created a local db, run `make setup` to bring up the database container, or `make setup-db` to bring up the container, apply database migrations and load fixture data.
- cd into the `/update_supply_chain_information` folder and run `python manage.py runserver`
- You must access the app on http://localhost:8000 as this is the URL which is configured as the 'redirect URL' for our authbroker credentials in staff SSO

### To just load fixture data:
- When you have your database container running and with up-to-date migrations, you can run `make load-data` to load fixture data into the database.

### To run tests:
- To run the suite of python unit tests, written in pytest, run `make tests`
- To run the suite of functional tests, using cypress, run `make functional-tests`. These run against DIT's [mock-sso](https://github.com/uktrade/mock-sso) application which runs in a docker container on port 8080. As mock-sso's `api/v1/user/me` endpoint returns [a specific user profile fixture](https://github.com/uktrade/mock-sso/blob/master/app/oauth/user.js#L51), the same fixture has been created for use in the functional tests at `cypress/fixtures/user.json`.

## Load testing

Load testing is carried out using preferred tool [Locust](https://locust.io/). Main focus of these tests are to find *max concurrent users*
that can be supported by the web app. Hence the test scenario is written to achieve just that.

Test specific configs are saved at *.locust.conf* while *load_test/locustfile.py* define the scenario.

### To start load test

- Start *dev* or *testserver* in one terminal
- Start locust tool in another terminal with below command

```python
locust --config .locust.conf
```

Refer to the tool's docs for more info on the flags used.

### Automated accessibility testing:
The project uses the [cypress-axe](https://github.com/component-driven/cypress-axe) package which allows for the automation of accessibility testing within tests written with cypress.

To add accessibility testing to a cypress spec:
- Add the command `cy.injectAxe()` after wherever `cy.visit(url)` is called. This injects the axe-core runtime into the page being tested.
- Add a test to check for accessibility issues on a page using the command `cy.runA11y()`. This will output details of any accessibility violations into a table in the terminal where cypress is running.

## Adding Black pre-commit hook

- Generate your pre-commit hooks by running `pre-commit install`.
- When commiting your files, there will be output from Black saying your file has failed, which kickstarts the autocorrector.
- Stage the files again with the Black corrections, and commit.

## Integrations

### Staff SSO
This project uses DIT's Staff SSO as it's authentication broker, which the app communicates with via [The Django Staff SSO client](https://github.com/uktrade/django-staff-sso-client). This provides a global session around DIT's projects, meaning they all share a centralised authentication. In this app, we extend the authentication slightly, in order to obtain and record the government department that a user should be assigned to. This is done using the domain from the email address in their Staff SSO profile.

