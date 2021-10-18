# Bar server
This is the server of the bar managment system.

## Requirements
You have to install `docker` and `docker-compose`.
Exemple for debian and other derivate linux distributions :
```bash
sudo apt install docker docker-compose
```

## Start
To start the server
```bash
docker-compose up -d
```

For devloppement you can start the server like this :
```bash
sudo docker-compose --env-file .env.dev up
```

The api root is accesible at [https://localhost/api/v0]

## Configuration
All configurations are in the `.env` file
Don't forget to change passwords for production use.

## Testing
To launch tests :
```bash
docker-compose -f ./docker-compose.test.yml run sut
```
