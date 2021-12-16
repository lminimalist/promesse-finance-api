# Promesse Finance API

Goal: create an apified version of Yahoo Finance where you can fetch JSON stocks data using HTTP (e.g https://hostname/AAPL/price) instead of manually downloding the csv from Yahoo Finance website.

![
](https://i.imgur.com/QD9pkZW.png)

## Project folder structure

### app.py

The main file that starts the web server
It imports all files + and instantiate the app

### /db

Credentials to connect to db

### /models

Define schema of the data stored in DB

### /resources

Code logic that handles incoming requests from the client

### /utils

Set of tools to scrape data, make heavy calculations (returns, correlations, ML)

### /tests

All tests code of the API

## How to run the API on localhost?

1. Clone the repo on your computer
2. Open your terminal and cd to the project folder
3. [Install Pipenv](https://docs.pipenv.org/en/latest/) (it manages python packages and dev environment)
4. Create a virtual environment
   `pipenv --python 3.7`
5. Activate your virtual environment
   `pipenv shell`
6. Install all project dependencies
   `pipenv install`
7. Run the web server
   `python src/app.py`

If everything is running well, you have to see the following message:

     * Serving Flask app "app" (lazy loading)
     * Environment: production
       WARNING: Do not use the development server in a production environment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

8. You can start testing the API via `http://127.0.0.1:5000/`

## How to use the API?
