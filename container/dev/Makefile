DJANGO_CONTAINER_NAME = coalb_web
NGINX_CONTAINER_NAME = coalb_nginx

server:
	docker exec -it $(NGINX_CONTAINER_NAME) bash

sh:
	docker exec -it $(NGINX_CONTAINER_NAME) sh

bash:
	docker exec -it $(DJANGO_CONTAINER_NAME) bash

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

reboot:
	docker-compose down && docker-compose up -d

logs:
	docker-compose logs

format:
	docker exec -it ${DJANGO_CONTAINER_NAME} flake8 --exclude=migrations --ignore=E121,E203,E226,E402,E501,F401,F403,W503 ./

test:
	docker exec -it ${DJANGO_CONTAINER_NAME} pytest

check:
	make format && make test
