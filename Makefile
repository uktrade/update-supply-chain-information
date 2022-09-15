build:
	docker-compose build

up:
	docker-compose up

up-d:
	docker-compose up -d

down:
	docker-compose down

migrations:
	docker-compose run --rm supply_chain python manage.py makemigrations supply_chains

migrate:
	docker-compose run --rm supply_chain python manage.py migrate

checkmigrations:
	docker-compose run --rm --no-deps supply_chain python manage.py makemigrations --check

all-requirements:
	docker-compose run --rm supply_chain pip-compile --output-file requirements/base.txt requirements.in/base.in
	docker-compose run --rm supply_chain pip-compile --output-file requirements/dev.txt requirements.in/dev.in
	docker-compose run --rm supply_chain pip-compile --output-file requirements/prod.txt requirements.in/prod.in

flake8:
	docker-compose run --rm --no-deps supply_chain flake8

black:
	docker-compose run --rm --no-deps supply_chain black .

first-use:
	docker-compose run --rm supply_chain python manage.py migrate
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
