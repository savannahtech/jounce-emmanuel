# homework

Make sure you have docker install

and then run docker-compose up --build -d to install dependencies and build the app

2. Once the build is successful visit this url
   http://localhost:8000/frontend/- from the frontend view

http://localhost:8000/api/rank/{metric_value} the endpoint that performs the ranking

http://localhost:8000/api/simulate to generate random data

Infrastructure:
I used Githulb Workflow to trigger a deployment when code is pushed to the main branch
`.github/workflows/ci.yml`

On the worker.py file, I initialized the queueing and consuming data from the queue, I also followed the solid design principles on that. The retry logic on the API is there too.
`worker.py`

key features: redis to cache and the cache is invalidated when the simulate endpoint is fire
SQLite: a lite database for storage
react and charjs for the frontend
fastApi for the API

