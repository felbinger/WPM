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
