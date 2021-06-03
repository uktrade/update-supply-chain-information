setup:
	docker-compose -f docker-compose.yaml up -d

setup-db: setup
	python update_supply_chain_information/manage.py migrate
	python update_supply_chain_information/manage.py createinitialrevisions
	# Remove the DIT gov department added in a data migration
	python update_supply_chain_information/manage.py flush --no-input
	make load-data

create-db: setup
	docker-compose exec db psql -h localhost -U postgres -c "CREATE DATABASE supply_chain_info WITH OWNER postgres ENCODING 'UTF8';"
	make setup-db

drop-db: setup
	docker-compose exec db psql -h localhost -U postgres -c "DROP DATABASE supply_chain_info"

tests:
	pytest update_supply_chain_information

load-data: setup
	python update_supply_chain_information/manage.py loaddata cypress/fixtures/*.json
	python update_supply_chain_information/manage.py datafixup --noinput

functional-tests:
	bash run_functional_tests.sh
