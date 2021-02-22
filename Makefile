setup:
	docker-compose up -d

create-db: setup
	docker exec defend-data-capture_db_1 psql -h localhost -U postgres -c "CREATE DATABASE defend WITH OWNER postgres ENCODING 'UTF8';"
	python api/manage.py migrate

drop-db: setup
	docker exec defend-data-capture_db_1 psql -h localhost -U postgres -c "DROP DATABASE defend"

tests: setup
	pytest api

load-data: setup
	python api/manage.py loaddata api/api/fixtures.json

