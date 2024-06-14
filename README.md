# celes-challenge
This project is the development of the technical assesment for backend engineer role at Celes.
The project is a sales microservice build with [FastAPI](https://fastapi.tiangolo.com/) that allows users to interact with an API in order to get relevant information about the sales.

## Requirements
- `docker > 26.0.0`
- `docker-compose` or `compose` plugin for Docker

## How to launch
The application is based on `Docker` helping to make sharing, building and launching the microservice easily. In order to launch the application in your local machine please follow the next steps:
1. Clone this repository
2. Copy the file `.env.example` to `.env` and adjust the values for your use
3. Inside the project directory run `docker-compose build && docker-compose up`
4. The microservice will be exposed through port `:8080`. This port could be changed in the `docker-compose.yml` file if needed.
5. Open your browser and go to `http://localhost:8080/docs` and you'll see the `Swagger` documentation of the microservice.

## Running unit tests
In order to execute the unit tests open a new terminal and run `docker exec celes-sales pytest . -v`

## Endpoints
The microservice expose 5 different endpoints with different puposes
### Health-check (/)
The root of the API. This endpoint is used as a health check status of the overall application. This endpoint just return a `HTTP 204 No Content` resonse if the service is available.

### Authentication
The service exposes to endpoints for handling authentication process through [Firebase](https://firebase.google.com/docs/auth/). Users must be authenticated in order to use the `/sales` and `/sales/period` endpoints.

#### Signup (/auth/signup)
Use this endpoint to create a valid user for using the API. The request body it's very simple just requires `email` and `password` values.
**Example**

Request:
```
curl --location 'http://localhost:8080/auth/signup' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "your-email@example.com",
    "password": "secret-password"
}'
```

Response:
```json
{
    "data": {
        "msg": "User created successfuly",
        "user_uuid": "9DOKz9n335hXHHoUIQS5b3GSKut1"
    },
    "error_details": null
}
```

#### Login (/auth/login)
This endpoint generates a valid JWT authentication token to be include in the requests. The request body requires `email` and `password` values.
**Example**
Request:
```
curl --location 'http://localhost:8080/auth/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "your-email@example.com",
    "password": "secret-password"
}'
```

Response:
```json
{
    "data": {
        "token_id": "eyJhbGciOiJSUzI1NiIsImtp...",
        "expires_in": "3600"
    },
    "error_details": null
}
```


### Sales by period (/sales/period)
In order to retrieve the total sales in a given period `/sales/period` is exposed. This endpoint requires `start_period` and `end_period` dates in the format `YYYY-MM-DD` and at least one of the following query keys:

- `key_employee`: Employee unique key
- `key_product`: Product unique key
- `key_store`: Store unique key

**Note:** Don't forget to include the JWT token as a header `Authorization eyJhbGciOiJSUzI1NiIsI...`

### Example:

**Request**
```
curl --location 'http://localhost:8080/sales/period?start_period=2023-10-03&end_period=2023-12-12&key_product=1|43085' \
--header 'Authorization: eyJhbGciOiJSUzI1NiIsImtp...'
```


**Response**
```json
{
  "data": {
    "amount": 147800.00
  },
  "error_details": null,
}
```

### Total and average sales (/sales)
If you want to fetch the total and average sales by store, product, employee or a combination of these, the `/sales` endpoint is the one that retrieves that info. Same as the above endpoint this one requires at least one of the following query keys:

- `key_employee`: Employee unique key
- `key_product`: Product unique key
- `key_store`: Store unique key


**Note:** Don't forget to include the JWT token as a header `Authorization eyJhbGciOiJSUzI1NiIsI...`

### Example:
**Request**
```
curl --location 'http://localhost:8080/sales?key_product=1|43085' \
--header 'Authorization: eyJhbGciOiJSUzI1NiIsImtp...'
```

**Response**
```json
{
    "data": {
        "total": 43227797.46,
        "average": 18465.52646732166
    },
    "error_details": null
}
```

## Design
The microservice is a FastAPI application exposing authentication and sales endpoints.  

The data source are build from separate chunks of `.parquet` files that are loaded at startup and cached for following uses by the microservice. This is a design decision in order to avoid several IO tasks during the microservice execution. (See `/app/dataloader.py`)

The core component of this microservice is the `SalesService` which provides functionalities for filtering sales data based on user-defined criteria and calculating total and average sales within the filtered data set.

### SalesService
The `SalesService` is the core component of the application it defines the business rules to fetch and calculate sales totals based on different filters received from the request query params.
The data source query is build chaining filter conditions with logical operator `AND`. `_filter_data(self, data: pd.DataFrame)` constructs a valid query string accepted by pandas dataframe `query()` method. This allows to having an extensible version to adding easily more filters if needed.

`_calc_total(data: pd.DataFrame)` is a private static method that calculates the total of sales of a given pandas dataframe (commonly the filtered one) by getting the product of quantity(`Qty`) and cost ammount (`CostAmount`) per each sale.

### Filter
`Filter` is a basic Python `dataclass` that holds relevant information related to an specific filter. A common `Filter` holds the key (dataframe column to be used for filtering), operator (acts as the comparisson approach to be used; Could be `eq: ==`, `gt: >`, `gte: >=`, `lt: <`, `lte: <=`), and finally the value. This approach provides flexibility for filtering creation

### FilterBuilder
`FilterBuilder` is a simple builder pattern implementation that allows to set a list of `Filter` objects to be used in the filtering process. It holds specific methods for `KeyEmployee`, `KeyProduct` and `KeyStore` filters and a more general `add_filter(filer: Filter)` to adding other kind of filters (Used by the periods filters)
