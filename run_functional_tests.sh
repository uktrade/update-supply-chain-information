#!/usr/bin/env bash

running_locally=${RUNNING_LOCALLY:-true}

# Bring up the db and mock-sso docker containers
docker-compose -f docker-compose.yaml -f docker-compose.override.yaml up -d

# Run the django application on port 8001 with fixtures for cypress
# Save the pid for the server to a file 'backend.pid'
# Run all cypress tests after a 5 second delay to allow the django server to be brought up
export SET_HSTS_HEADERS='False'

# reset db before test run
make drop-db && make create-db

python update_supply_chain_information/manage.py runserver \
    --settings=test_settings \
    8001 \
    & echo $! > backend.pid \
    & (sleep 5 && npx cypress run --headless --browser chrome)

cypress_failed=$?

if [ "$running_locally" == true ]; then
    # Kill the application using the pid previously saved
    kill $(cat backend.pid)
    # Drop the test database
    make drop-db && make create-db
fi

exit $cypress_failed
