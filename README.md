# Grid Training: Capstone
This is a submission for the Capstone project given for the grid training.

## Running the project
Input these commands to the host machine
```
docker network create docker-net
docker pull postgres
docker run --rm --name pg-docker --network docker-net -e POSTGRES_PASSWORD=docker -e POSTGRES_DB=harvester_api -d -v $PWD/data/db:/var/lib/postgresql/data:Z postgres
docker build ./harvester_api -t harvester_api
docker build ./harvester_app -t harvester_app
docker run --rm  --name harvester_api --network docker-net  -v $PWD/data/api:/app/downloads:Z -d harvester_api
```
After which run the next command whenever you wish to scrape the site
```
docker run --rm  --name harvester_app --network docker-net  -v $PWD/data/app:/app/downloads:Z -it harvester_app
```

## How to test
Clone the ```unit_testing``` brach of the repository to use for testing

Start a local postgres server with a password of ```docker```. Try using PgAdmin4

Run ```pytest --cov=. test/``` inside ```capstone/harvester_app/```

test