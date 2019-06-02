# Open Distro for Elasticsearch with MQTT
Open Distro for Elasticsearch stack running in Docker just for testing purposes.

### Usage with docker-compose

Start the environment:
```
docker-compose up
```

Open Kibana Web interface: 
```
http://localhost:5601/
```

# Open Distro for Elasticsearch with Traefik and MQTT
Open Distro for Elasticsearch stack running in Docker with Traefik as Reverse Proxy. Traefik handles traffic to Kibana Web Interface. Elasticsearch persist it's data to Docker volume. Health checks of the Kibana and Elasticsearch services is also included.

### Usage with docker-compose in production
Note: you must replace the domain `kibana.mysite.com` in files `docker-compose-production.yml` and `traefik.toml`

Create docker network for traefik:
```
docker network create traefik-network
```

Start the environment:
```
docker-compose -f docker-compose-production.yml up
```
Open Kibana Web interface or Traefik Dashboard using the address: 
```
http://kibana.mysite.com/
http://kibana.mysite.com:8080/
```
Kibana uses initial username `admin` and password `admin`