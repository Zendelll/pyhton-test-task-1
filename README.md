# pyhton-test-task-1
Test task for one company (I won't specify c: )

# .env
I intentionally put .env file into the repository, because I use minio and don't have anything important there, but it could simplify initial setup of the app.

# Start app
To start you can use docker-compose or, additionaly, you can use a dockerfile to start without MinIO, if you don't need it. 

Also there is a script to create a test bucket to simplify testing of this app (scripts/create_test_bucket.py). 
It runs on the container startup if env variable "MINIO" equals "true" and creates "BUCKET_NAME" bucket (if bucket already exsists, nothing happens)

So to simplify, just use command below to run app without extra setup

```
docker-compose up -d --build
```

# Test
I also wrote some unit tests for the app. To run them, firstly, setup virtual enviroment (venv), using requirements.txt and dev_requirements.txt files

Then simply run command below

```
pytest
```
