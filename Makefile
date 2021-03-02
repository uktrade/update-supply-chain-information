setup:
	docker-compose up -d

create-db: setup
	docker exec defend-data-capture_db_1 psql -h localhost -U postgres -c "CREATE DATABASE defend WITH OWNER postgres ENCODING 'UTF8';"
	python defend_data_capture/manage.py migrate

drop-db: setup
	docker exec defend-data-capture_db_1 psql -h localhost -U postgres -c "DROP DATABASE defend"

tests: setup
	pytest defend_data_capture

load-data: setup
	python defend_data_capture/manage.py loaddata defend_data_capture/fixtures.json

