setup:
	docker-compose up -d

setup-db: setup
	python defend_data_capture/manage.py migrate
	python defend_data_capture/manage.py createinitialrevisions
	make load-data

create-db: setup
	docker-compose exec db psql -h localhost -U postgres -c "CREATE DATABASE defend WITH OWNER postgres ENCODING 'UTF8';"
	make setup-db

drop-db: setup
	docker-compose exec db psql -h localhost -U postgres -c "DROP DATABASE defend"

tests:
	pytest defend_data_capture

load-data: setup
	python defend_data_capture/manage.py loaddata defend_data_capture/fixtures.json

