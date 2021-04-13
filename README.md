# Python Django Deployment Template
This template has been created for easy deployment of django applications, feel free to use it for other frameworks than django as well.

Make sure to enabled improved container support in feature preview. Don't forget to change the image name in [`.github/workflows/ci.yaml`](./.github/workflows/ci.yaml)

## Installation
First you need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)  
After you have started the services (`docker-compose up -d`), you can collect the static files and create a superuser account:  
```bash
# collect static files
docker-compose exec -u0 django /bin/sh -c 'python manage.py collectstatic --no-input'

# create superuser
docker-compose exec django /bin/sh -c 'python manage.py createsuperuser --username=admin --email=admin@example.de'
```

Afterwards you can access the application: [http://localhost:8080](http://localhost:8080)  
You can change the port inside the [`docker-compose.yml`](./docker-compose.yml#L29)

## Docker Image Flavors

**You can use three database types:**
- MariaDB  
- PostgreSQL  
- SQLite3 (You should only use sqlit3 for testing purpose)  

**You can use three authentication sources:**
- Local (Django) Authentication
- OpenLDAP
- OAuth (If your using pytemplate, you need to implement the required functions inside the django app yourself)

The schema for the docker tags is: `xxxxxx/yyyyyy:version-dbms-auth`:
- `felbinger/pytemplate:latest-sqlite3-localauth`
- `felbinger/pytemplate:latest-mariadb-localauth`
- `felbinger/pytemplate:latest-postgres-localauth`
- `felbinger/pytemplate:latest-sqlite3-openldap`
- `felbinger/pytemplate:latest-mariadb-openldap`
- `felbinger/pytemplate:latest-postgres-openldap`
- `felbinger/pytemplate:latest-sqlite3-oauth2`
- `felbinger/pytemplate:latest-mariadb-oauth2`
- `felbinger/pytemplate:latest-postgres-oauth2`


- `felbinger/pytemplate:edge-sqlite3-localauth`
- `felbinger/pytemplate:edge-mariadb-localauth`
- `felbinger/pytemplate:edge-postgres-localauth`
- `felbinger/pytemplate:edge-sqlite3-openldap`
- `felbinger/pytemplate:edge-mariadb-openldap`
- `felbinger/pytemplate:edge-postgres-openldap`
- `felbinger/pytemplate:edge-sqlite3-oauth2`
- `felbinger/pytemplate:edge-mariadb-oauth2`
- `felbinger/pytemplate:edge-postgres-oauth2`  

As default (`latest` / `edge`) the `postgres` database and the `localauth` is being used:
- `felbinger/pytemplate:latest`
- `felbinger/pytemplate:edge`
