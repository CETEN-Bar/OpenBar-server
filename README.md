# OpenBar server
This is a REST server giving an API to manage for a point of sale with managed storage and the users make themselves the order.
It was made for the "Bar" student club of TELECOM Nancy.
The project is now WIP. It should not be use in production.

## Requirements
You have to install `docker` and `docker-compose`.
Exemple for debian and derivative linux distributions :
```bash
sudo apt install docker-compose
```
More information here : [https://docs.docker.com/engine/install/debian/]


## Start
First copy the `.env.example` file to `.env` and change the passwords inside.

Then to start the server
```bash
docker-compose up -d
```

For development, you can use a `.env.dev` (cf `.env.dev.example`) and start the server like this :
```bash
sudo docker-compose --env-file .env.dev up
```
By default `.env.dev up` will automatically reload ths server on code changes. 

The api root is accessible at [http://localhost:8080/api/v0]

## Configuration
The main configurations are in the `.env` file.
Don't forget to change passwords for production use.

There is also `openbar/app/config.py` for more complicated config (like user token lifespan). Be careful with those.

## Testing
To launch tests :
```bash
docker-compose -f ./docker-compose.test.yml run sut
```
