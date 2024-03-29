build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

migrations:
	docker-compose run --rm supply_chain python manage.py makemigrations supply_chains

migrate:
	# This is bit hacky, but on a first time run on a new container the migrations seemed to reliably fail...
	docker-compose run --rm supply_chain echo "Making sure the container is fully up before we try to run the migrations" && sleep 2
	docker-compose run --rm supply_chain python manage.py migrate

checkmigrations:
	docker-compose run --rm --no-deps supply_chain python manage.py makemigrations --check

all-requirements:
	docker-compose run --rm supply_chain poetry lock
	docker-compose run --rm supply_chain poetry export --without-hashes -f requirements.txt -o requirements.txt
	docker-compose run --rm supply_chain poetry export --dev --without-hashes -f requirements.txt -o requirements-dev.txt

flake8:
	docker-compose run --rm --no-deps supply_chain flake8

black:
	docker-compose run --rm --no-deps supply_chain black .

first-use:
	make migrate
	docker-compose run --rm supply_chain python manage.py createinitialrevisions
	# Remove the DIT gov department added in a data migration
	docker-compose run --rm supply_chain python manage.py flush --no-input
	make load-data

load-data:
	docker-compose run --rm supply_chain python manage.py loaddata fixtures/*.json
	docker-compose run --rm supply_chain python manage.py datafixup --noinput

test:
	docker-compose run --rm supply_chain pytest /app --capture=no

bash:
	docker-compose run --rm supply_chain bash

shell:
	docker-compose run --rm supply_chain python manage.py shell
