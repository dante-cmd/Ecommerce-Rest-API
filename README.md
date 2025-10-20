# E-commerce Backend API

A complete e-commerce backend API built with FastAPI and SQLAlchemy, containerized with Docker.

## Features

- User management (registration, authentication)
- Product management (CRUD operations)
- Shopping cart functionality with user isolation
- Order processing
- MSSQL database support using pymssql driver

## Prerequisites

- Docker and Docker Compose installed

## Getting Started

1. Clone the repository
2. Navigate to the project directory
3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`

## Database Connection

This application uses pymssql driver to connect to MSSQL, which does not require ODBC drivers.

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
ecommerce_app/
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Core utilities (security, config)
│   ├── database/     # Database configuration
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas for validation
│   └── main.py       # FastAPI application entry point
├── tests/            # Test files
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. Register a new user with `POST /api/users/`
2. Log in with `POST /api/users/token` to get an access token
3. Include the token in the Authorization header for protected endpoints:
   ```
   Authorization: Bearer your-access-token-here
   ```

## Endpoints

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create a new product
- `GET /api/products/{id}` - Get a specific product
- `PUT /api/products/{id}` - Update a product
- `DELETE /api/products/{id}` - Delete a product

### Users
- `POST /api/users/` - Register a new user
- `POST /api/users/token` - Log in and get access token
- `GET /api/users/` - List all users
- `GET /api/users/{id}` - Get a specific user

### Cart (Protected - Requires Authentication)
- `GET /api/cart/` - Get current user's cart
- `POST /api/cart/` - Add item to cart
- `PUT /api/cart/{id}` - Update cart item
- `DELETE /api/cart/{id}` - Remove item from cart

### Orders (Protected - Requires Authentication)
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create a new order
- `GET /api/orders/{id}` - Get a specific order
- `PUT /api/orders/{id}` - Update order status

## Usage Examples

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed examples of how to use the API.

## Development

To run the application locally without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development dependencies
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Testing

To run the tests:
```bash
pytest
```

To run tests with coverage:
```bash
pytest --cov=app
```

## License

This project is licensed under the MIT License.