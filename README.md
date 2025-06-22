# Price Monitoring and Scraper System

This project is a system for price monitoring and data collection of products on external sales websites, such as OLX, Mercado Livre, Enjoei, and Estante Virtual. It consists of a FastAPI backend and a scrapers module that uses Celery for asynchronous tasks.

## System Structure

- **API Backend**: Manages products, search settings, and users.
- **Scrapers Module**: Collects product data from external sites.
- **Database**: Stores information about products, users, price history, and settings.
- **Celery**: Manages asynchronous and scheduled tasks.

## Running the Project

### Install Docker

1. Make sure you have Docker and Docker Compose installed. Follow the instructions on the [Docker website](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) to install Docker.
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

### Accessing the API

1. Access the API at http://localhost:8000/docs for the Swagger UI or http://localhost:8000/redoc for the ReDoc documentation.
   - You will be able to see the available endpoints and test them directly from the browser.
   - To test the endpoints you need first to create a user using the `/register` endpoint, then it's needed to authenticate using the `/auth/login` endpoint to obtain a token. Once you have the token, you can use it to access the other endpoints by including it in the `Authorization` header as a Bearer token (set the auth token in the `Authorize` button in the Swagger UI).
2. **(Optional)**. You can run **load_fixtures.py** to populate the database with initial testing data:
   ```bash
   docker exec -it web python3 src/scripts/load_fixtures.py all
   ```
3. **(Optional)**. If you want to test running the scrapers manually, you can execute the following commands to start the scrapers:
   ```bash
   docker exec -it web celery -A src.product_scrapers.celery.tasks call src.product_scrapers.celery.tasks.run_scraper_searches --args '["mercado_livre"]'
   ```
   In this example, we are running the scrapers for Mercado Livre. You can replace the arguments with other scrapers as needed.

### Features

- **Product Management**: Add, edit, and remove products.
- **Price History**: View the price history of collected products.
- **Search Settings**: Define parameters for data collection.
- **Authentication**: Manage users and authentication.
