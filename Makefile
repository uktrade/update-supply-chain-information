setup:
	docker-compose -f docker-compose.yaml up -d

setup-db: setup
	python update_supply_chain_information/manage.py migrate
	python update_supply_chain_information/manage.py createinitialrevisions
	make load-data

create-db: setup
	docker-compose exec db psql -h localhost -U postgres -c "CREATE DATABASE defend WITH OWNER postgres ENCODING 'UTF8';"
	make setup-db

drop-db: setup
	docker-compose exec db psql -h localhost -U postgres -c "DROP DATABASE defend"

tests:
	pytest update_supply_chain_information

load-data: setup
	python update_supply_chain_information/manage.py loaddata cypress/fixtures/*.json

functional-tests:
	sh run_functional_tests.sh
