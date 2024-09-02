# pyhton-test-task-1
Test task for one company (I won't specify c: )

# .env
I intentionally put .env file to the repo, because I use minio and don't have anything important there, but it could simplify initial set up of the app.

# Start app
To start you can use dockerfile or docker-compose to start with minio container.

Also there is script to create test bucket to simplify testing of this app (scripts/create_test_bucket.py). 
It runs on container startup if env variable "MINIO" equals "true" and creates "BUCKET_NAME" bucket (if bucket already exsists nothing happens)

So to simply run app without extra setup just use command below

```
docker-compose up -d --build
```

# Test
I also wrote some unit tests for an app. To run them firstly setup virtual enviroment (venv) using requirements.txt and dev_requirements.txt files

Then simply run command

```
pytest
```