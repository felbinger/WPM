# Wireguard Peer Manager

## Installation
First you need to install [docker](https://docs.docker.com/engine/install/) 
and [docker-compose](https://docs.docker.com/compose/install/)  
After you have started the services (`docker-compose up -d`), 
you can collect the static files and create a superuser account:  
```bash
# collect static files
docker-compose exec -u0 wpm /bin/sh -c 'python manage.py collectstatic --no-input'

# create superuser
docker-compose exec wpm /bin/sh -c 'python manage.py createsuperuser --username=admin --email=admin@example.de'
```

Afterwards you can access the application: [http://localhost:8080](http://localhost:8080)  
You can change the port inside the [`docker-compose.yml`](./docker-compose.yml#L29)


## Current News
This app is in an early stage of development. It's hosted on: [the general vm on pve2](https://wpm.general.pve2.secshell.net).
The vyos integration hasn't been implemented yet, so the commands will only be printed...

Don't forget to adjust keycloak authentication flow (role and workflow has already been created, but need to be adjusted...)
