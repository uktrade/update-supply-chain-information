# update-supply-chain-information

A Django app focused on collecting data about the UK's most valuable supply chains. This app is primarily a form in which other government departments can submit updates and provide information about the supply chains they manage.

The app uses the standard Django MVC architecture, alongside some Django REST framework end-points. These end-points will allow for the future development of a pipeline that will feed the app's data into [Data Workspace](https://data.trade.gov.uk/). This data will later serve a series of visualisations which will be hosted on Data Workspace.

## Running the app and its tests

Docker is required to run this project and the project use docker compose extensively.

The project uses a `Makefile` to make running commands easier. `make` commands need to be run at the same directory level as the Makefile.

### Setting up environment variables:
- Environment variables can be found in the `.env.example`
- Copy these to a `.env` file in the root folder
- The `AUTHBROKER_CLIENT_ID` and `AUTHBROKER_CLIENT_SECRET` values needed for staff SSO can be found in [passman](https://passman.ci.uktrade.digital/secret/61f0a3bf-33f3-427e-8ade-cdee0c637031/)

### Setting up static files
The project uses [webpack](https://webpack.js.org/) to build static files, to setup:
- Install node version 18.x
- Run `npm install` to install all node modules, including webpack and the govuk-frontend npm package
- Run `npm run dev` - webpack will then bundle all static files in `assets` and create 'bundles' in `assets/webpack_bundles`. When making changes to static files, e.g. updating `application.scss`, webpack will recompile the files when edited and create a new bundle. You can quit this process when it's complete if you are not going to be working on things that would need recompiling.

### Styles
The project mainly uses styles from the [govuk-frontend](https://github.com/alphagov/govuk-frontend) npm package. Examples of how to use these styles can be found in components on the [GOVUK design system](https://design-system.service.gov.uk/components/).

Where it is not possible to use a govuk style, the [moj-frontend](https://github.com/ministryofjustice/moj-frontend) library (an extension of govuk-frontend) has been used, and any custom styles added to `assets/application.scss`, with classes prefixed with `.app-`.

### To run the app for the first time:
- run `make build`
- run `make first-use`
- run `make up`
- You must access the app on http://localhost:8000 as this is the URL which is configured as the 'redirect URL' for our authbroker credentials in staff SSO
- Note: Being connected to the VPN can lead to http://localhost:8000 to fail to load. Disconnect to test locally.

### To just load fixture data:
- Run `make load-data` to load fixture data into the database.

### To run tests:
- To run the suite of python unit tests, written in pytest, run `make test`

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

## Adding Black pre-commit hook

- Generate your pre-commit hooks by running `pre-commit install`.
- When committing your files, there will be output from Black saying your file has failed, which kickstarts the autocorrector.
- Stage the files again with the Black corrections, and commit.

## Integrations

### Staff SSO
This project uses DIT's Staff SSO as it's authentication broker, which the app communicates with via [The Django Staff SSO client](https://github.com/uktrade/django-staff-sso-client). This provides a global session around DIT's projects, meaning they all share a centralised authentication. In this app, we extend the authentication slightly, in order to obtain and record the government department that a user should be assigned to. This is done using the domain from the email address in their Staff SSO profile.

### Activity Stream, Data Flow, and Data Workspace

#### Activity Stream

The `activity_stream` app provides a feed of the project's data in [Activity Streams 2.0](https://www.w3.org/TR/activitystreams-core/) format, for consumption by the DIT's Activity Stream.
Activity Stream then makes the data available in its Elasticsearch instance.

As Activity Stream uses Hawk authentication, the following environment variables must be set to support this:

* `HAWK_UNIQUE_ID` - A value used internally to identify the credentials used to access the feed.
  This can be an informative name, as it appears as part of the name autogenerated for Activity Stream Elasticsearch's internal indices.
* `HAWK_SECRET_ACCESS_KEY` - A shared secret used by Activity Stream to encrypt its requests, and by the `activity_stream` app to authenticate those requests.
A suitable value for this can be generated the same way as a Django Secret Key using `django.utils.crypto.get_random_string()` with a `length` of 64.

The same values, along with several other variables, must then be [provided to Activity Stream in Vault](https://vault.ci.uktrade.digital/ui/vault/secrets/dit%2Factivity-stream/list/activity-stream/),
to configure its access to the feed. The `nn` in the environment variable names below denotes a numeric value 
which is internal to Activity Stream; when configuring such values, 
simply use the next highest number after the values used by already-configured feeds.

* `FEEDS__nn__ACCESS_KEY_ID`: `usci_activitystream`
* `FEEDS__nn__UNIQUE_ID`: `{the value of HAWK_UNIQUE_ID above}`
* `FEEDS__nn__SECRET_ACCESS_KEY`: `{the value of HAWK_SECRET_ACCESS_KEY above}`
* `FEEDS__nn__SEED`: `https://{domain}/api/activity-stream/`
* `FEEDS__nn__TYPE`: `activity_stream`

For more information about configuring integration with Activity Stream, see [the Activity Stream documentation](https://readme.trade.gov.uk/docs/services/activity-stream.html).

For additional support in configuring integration, including being given access to their Vault, contact the Data Integrations team on Slack via [the #di-pipelines channel](https://ditdigitalteam.slack.com/archives/CUT4MMBQD).

#### Data Flow

Once the project data has been made available in Activity Stream's Elasticsearch, it can be extracted
by the DIT's Data Flow application which stores it in Data Workspace. Once in Data Workspace, it can be used by 
the Supply Chains Visualisations application.

This integration is achieved by the creation of multiple DAGs (Python classes based on Airflow DAGs),
with each DAG corresponding to one of the models serialised by `activity_stream`,
in accordance with the general process described in [How to get data into a table in Data Workspace](https://readme.trade.gov.uk/docs/howtos/data-workspace-pipeline.html).

The DAGS implemented for this project follow the pattern set by other DAGs in the Data Flow application that consume Activity Stream data,
which can be found [in Data Flow's GitHub repository](https://github.com/uktrade/data-flow/blob/master/dataflow/dags/activity_stream_pipelines.py).
Each DAG stores the data it retrieves in a Data Workspace table corresponding to the type of the model retrieved.

It is expected that a complete DAG run, resulting in the data from this project becoming available in Data Workspace,
will happen daily. Should more or less frequent updates be required, this must be configured by the Data Integrations team. 

#### Data Workspace

Details of deploying an application to use this project's data after it has travelled into Data Workspace via the above route
can be found in [How to use Data Workspace datasets in your application](https://readme.trade.gov.uk/docs/howtos/data-workspace-datasets.html).

Note that Data Workspace presents data tables in a flat form - it does not use Foreign Key relationships.
As this project uses UUIDs as primary keys, it is still possible to follow relationships within Data Workspace,
but this would have to be implemented at the application level.


## Links to Analyses

The data gathered by this service are used to create a number of dashboards in Data Workspace.
These are linked to from the "Analysis" section of the home page of the service.

### Adding a Link

* Add the link to Vault under a suitable name; this makes it available in the deployment environment.
* In `config/settings/base.py` add the link as a setting, obtaining the value from the environment.
* In `supply_chains.templatetags.supply_chain_tags` add a template tag that renders the content of the setting.
* In `supply_chains/templates/supply_chains/index.html` copy and paste one of the existing visualisation link blocks,
updating the title, description, and template tag used for rendering the link's `href` attribute appropriately.
* Update `env.example` to include the new value.
* For local development, add the new value in your `.env` file.
