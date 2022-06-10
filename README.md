# Wireguard Peer Manager

## Installation
First you need to install [docker](https://docs.docker.com/engine/install/) 
and [docker-compose](https://docs.docker.com/compose/install/)  
After you have started the services (`docker-compose up -d`), 
you can collect the static files and create a superuser account:  
```bash
# collect static files
docker-compose exec -u0 django /bin/sh -c 'python manage.py collectstatic --no-input'

# create superuser
docker-compose exec django /bin/sh -c 'python manage.py createsuperuser --username=admin --email=admin@example.de'
```

Afterwards you can access the application: [http://localhost:8080](http://localhost:8080)  
You can change the port inside the [`docker-compose.yml`](./docker-compose.yml#L29)


## Dev Information
This app is in an early stage of development. OpenID Connect (OIDC / OAuth2) doesn't work yet with Keycloak.  
You can log in and use the app by creating a superuser account, afterwards you can log in (`/admin/login`).  
Now you have a session and can use it.

The integration for vyos hasn't been implemented yet.  
The vyos commands that the application would execute later on, are shown in stdout / `print()`
