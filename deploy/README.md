## Sample Deploy environment

this directory contains samples that you can use to deploy this project

> Certificates are fake

Customize files and run it using `docker-compose`

### files:

- `nginx.conf` contains configurations related to NginX (as a webserver)
- `docker-compose.yaml` a simple `Compose` file with `nginx`, `metabase` and `metabase-search`
- `docker-compose.build.yaml` used for local development

> other files are just some files needed for SSL (You have to use Real certs in production)
