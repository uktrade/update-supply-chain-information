build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

migrations:
	docker-compose run --rm supply_chain python manage.py makemigrations

first-use:
	docker-compose run --rm supply_chain python manage.py migrate
	docker-compose run --rm supply_chain python manage.py createinitialrevisions
	# Remove the DIT gov department added in a data migration
	docker-compose run --rm supply_chain python manage.py flush --no-input
	make load-data

load-data:
	docker-compose run --rm supply_chain python manage.py loaddata cypress/fixtures/*.json
	docker-compose run --rm supply_chain python manage.py datafixup --noinput

tests:
	pytest update_supply_chain_information
