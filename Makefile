CONTAINER_NAME_DJANGO := coalb_web
CONTAINER_NAME_NGINX := coalb_nginx

sh:
	docker exec -it $(CONTAINER_NAME_NGINX) sh

server:
	docker exec -it $(CONTAINER_NAME_NGINX) bash

bash:
	docker exec -it $(CONTAINER_NAME_DJANGO) bash

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
	docker exec -it ${CONTAINER_NAME_DJANGO} flake8 --exclude=migrations --ignore=E121,E203,E226,E402,E501,F401,F403,W503 ./

test:
	docker exec -it ${CONTAINER_NAME_DJANGO} pytest

check:
	make format && make test
