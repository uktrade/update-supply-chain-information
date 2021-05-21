#!/usr/bin/env bash

running_locally=${RUNNING_LOCALLY:-true}

# Bring up the db and mock-sso docker containers
docker-compose -f docker-compose.yaml -f docker-compose.override.yaml up -d

# Run the django application on port 8001 with fixtures for cypress
# Save the pid for the server to a file 'backend.pid'
# Run all cypress tests after a 5 second delay to allow the django server to be brought up
python defend_data_capture/manage.py testserver \
    --addrport 8001 \
    --settings=test_settings \
    --noinput \
    cypress/fixtures/govDepartment.json cypress/fixtures/user.json \
    cypress/fixtures/supplyChains.json cypress/fixtures/strategicActions.json \
    cypress/fixtures/strategicActionUpdates.json \
    & echo $! > backend.pid \
    & (sleep 5 && npx cypress run --headless --browser chrome)

cypress_failed=$?

if [ "$running_locally" == true ]; then
    # Kill the application using the pid previously saved
    kill $(cat backend.pid)
    # Drop the test database
    docker-compose exec db psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS test_defend"
fi

exit $cypress_failed
