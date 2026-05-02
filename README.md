# E-commerce Backend API

A complete e-commerce backend API built with FastAPI and SQLAlchemy, containerized with Docker. It includes user and product management, IP-based cart tracking, order processing, user interaction analytics, and a Markov-chain user journey simulator.

## Features

- **User management** — registration, authentication (with and without password for simulations), admin roles
- **Product management** — full CRUD operations with random listing for discovery simulation
- **IP Address tracking** — register and track client IP addresses independently of users
- **User-IP associations** — link IP addresses to registered users for cross-device tracking
- **Shopping cart** — IP-based cart isolation (works for both anonymous and logged-in users)
- **Order processing** — authenticated checkout with stock deduction and payment method recording
- **Interaction tracking** — record user journey events (views, clicks, add_to_cart, checkout, purchase, exit, etc.)
- **User journey simulation** — Markov-chain based scheduler that simulates realistic e-commerce funnel behavior
- **MSSQL database support** using the `pymssql` driver (no ODBC required)

## Prerequisites

- Docker and Docker Compose (recommended)
- Python 3.11+ (for local development)

## Getting Started

### With Docker Compose

1. Clone the repository
2. Navigate to the project directory
3. Start the services:
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`.

Docker Compose spins up two services:
- `sqlserver` — Microsoft SQL Server 2019
- `app` — the FastAPI application with auto-reload via bind mount

### Environment Variables

The app reads the following environment variables (defaults are set for the Docker Compose setup):

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_SERVER` | `sqlserver` | MSSQL host |
| `DB_DATABASE` | `ecommerce_db` | Database name |
| `DB_USERNAME` | `sa` | Database user |
| `DB_PASSWORD` | `YourStrong@Passw0rd` | Database password |
| `SKIP_DB_INIT` | — | Set to `true` to skip the DB creation wait loop (useful for tests) |

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
├── app/
│   ├── api/               # API route handlers (cart, interactions, ip_address, orders, products, users, user_ip_address)
│   ├── core/              # Security utilities (JWT, password hashing, auth dependencies)
│   ├── database/          # SQLAlchemy engine, session, and base
│   ├── models/            # Database ORM models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── create_db.py       # Database creation helper
│   ├── init_db.py         # Seed sample products, users, IPs, and an admin account
│   ├── main.py            # FastAPI application entry point
│   ├── customers.csv      # Sample customer data
│   └── products.csv       # Sample product catalog
├── tests/
│   ├── conftest.py        # Pytest fixtures (in-memory SQLite override)
│   └── test_main.py       # Full API test suite
├── venv/                  # Python virtual environment
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── scheduled_user_journey.py   # Markov-chain journey simulator
├── matrix_transition.json      # Transition probabilities for the simulator
├── notebook.ipynb
├── ECOMMERCE_FUNNEL.md         # E-commerce funnel benchmark guide
├── USAGE_EXAMPLES.md           # Spanish-language cURL examples
└── README.md
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

### IP Address
- `POST /api/ip_address/` — Register a new IP address
- `GET /api/ip_address/` — List IP addresses (random order)
- `GET /api/ip_address/{ip_address}` — Get a specific IP by address string

### Users
- `POST /api/users/` — Register a new user
- `POST /api/users/token` — Log in and get an access token (password required)
- `POST /api/users/token_without_password` — Log in and get an access token (email only; simulation helper)
- `GET /api/users/` — List all users
- `GET /api/users/{id}` — Get a specific user
- `GET /api/users/email/{email}` — Get a user by email

### User IP Address
- `POST /api/user_ip_address/` — Associate a user with an IP address
- `GET /api/user_ip_address/` — List associations (random order)
- `GET /api/user_ip_address/{ip_address_id}` — Get association by IP ID

### Products
- `GET /api/products/` — List products (random order; supports `skip` / `limit`)
- `POST /api/products/` — Create a new product
- `GET /api/products/{id}` — Get a specific product (supports `quantity` availability check)
- `PUT /api/products/{id}` — Update a product
- `DELETE /api/products/{id}` — Delete a product

### Cart (IP-based — no authentication required)
- `GET /api/cart/{ip_address_id}` — Get cart for an IP address
- `POST /api/cart/` — Add item to cart
- `PUT /api/cart/` — Update cart item quantity
- `DELETE /api/cart/` — Remove item from cart

### Orders (Protected — Requires Authentication)
- `GET /api/orders/` — List orders (admins see all; users see their own)
- `POST /api/orders/` — Create a new order from cart items
- `GET /api/orders/{id}` — Get a specific order
- `PUT /api/orders/{id}` — Update order status

### Interactions
- `POST /api/interactions/` — Record an interaction (open endpoint)
- `GET /api/interactions/` — List interactions (admin only)
- `GET /api/interactions/{id}` — Get a specific interaction (admin only)

## User Journey Simulation

The project includes a sophisticated e-commerce funnel simulator (`scheduled_user_journey.py`) that models realistic user behavior using a Markov chain defined in `matrix_transition.json`.

Supported journey states:
- `start`, `landing_page`, `search`, `category_view`, `product_view`
- `add_to_cart`, `cart_view`, `remove_from_cart`
- `checkout_started`, `login_required`, `shipping_info`, `payment_info`
- `purchase`, `exit`

Run the simulator locally:

```bash
python scheduled_user_journey.py
```

It will schedule simulations every few seconds, generating users, IP addresses, cart actions, orders, and interaction events automatically against the running API.

## Usage Examples

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed cURL examples (in Spanish).

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

3. Ensure you have an accessible MSSQL instance (or override the DB settings via environment variables).

4. Run the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Testing

The test suite uses an in-memory SQLite database so no SQL Server instance is required.

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app
```

Run a specific test file verbosely:
```bash
pytest tests/test_main.py -v
```

## Database Schema

Key entities:
- **IPAddress** — stores unique IP addresses
- **User** — registered accounts with optional admin flag
- **UserIPAddress** — many-to-one link between users and IPs
- **Product** — catalog items with stock and availability
- **CartItem** — IP-based cart entries
- **Order / OrderItem** — purchased items with snapshot pricing
- **Interaction** — funnel events tied to an IP address

See `app/models/models.py` for the full schema definition.

## License

This project is licensed under the MIT License.
