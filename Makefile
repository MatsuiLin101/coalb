DJANGO_CONTAINER_NAME = coalb_dg
NGINX_CONTAINER_NAME = coalb_ng

bash:
		docker exec -it $(DJANGO_CONTAINER_NAME) bash

server:
		docker exec -it $(NGINX_CONTAINER_NAME) bash

sh:
		docker exec -it $(NGINX_CONTAINER_NAME) sh
