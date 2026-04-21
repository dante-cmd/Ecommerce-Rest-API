# Ejemplo de uso de la API

Este documento muestra cómo usar la API de e-commerce, incluyendo autenticación, gestión de productos, carrito e interacciones.

## 1. Registro de usuario

```bash
curl -X POST "http://localhost:8000/api/users/" \
     -H "Content-Type: application/json" \
     -d '{"email": "newuser@example.com", "username": "newuser", "password": "password123"}'
```

## 2. Inicio de sesión

```bash
curl -X POST "http://localhost:8000/api/users/token" \
     -H "Content-Type: application/json" \
     -d '{"email": "newuser@example.com", "password": "password123"}'
```

Esto devolverá un token de acceso:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 3. Gestión de productos

### Crear un nuevo producto (solo administradores)

```bash
curl -X POST "http://localhost:8000/api/products/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Nuevo producto",
           "description": "Descripción del nuevo producto",
           "price": 29.99,
           "category": "Electronics",
           "stock_quantity": 100,
           "is_available": true
         }'
```

### Listar todos los productos

```bash
curl -X GET "http://localhost:8000/api/products/"
```

### Obtener un producto específico

```bash
curl -X GET "http://localhost:8000/api/products/1"
```

### Actualizar un producto (solo administradores)

```bash
curl -X PUT "http://localhost:8000/api/products/1" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Producto actualizado",
           "price": 39.99
         }'
```

## 4. Carrito de compras (requiere autenticación)

### Agregar un producto al carrito:

```bash
curl -X POST "http://localhost:8000/api/cart/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{"product_id": 1, "quantity": 2}'
```

### Ver el carrito:

```bash
curl -X GET "http://localhost:8000/api/cart/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Actualizar un item del carrito:

```bash
curl -X PUT "http://localhost:8000/api/cart/1" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{"quantity": 3}'
```

### Eliminar un item del carrito:

```bash
curl -X DELETE "http://localhost:8000/api/cart/1" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 5. Órdenes (requiere autenticación)

### Crear una nueva orden:

```bash
curl -X POST "http://localhost:8000/api/orders/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
           "items": [
             {"product_id": 1, "quantity": 2},
             {"product_id": 2, "quantity": 1}
           ],
           "payment_method": "credit_card",
           "bank": "Visa"
         }'
```

### Ver todas las órdenes (solo administradores pueden ver todas):

```bash
curl -X GET "http://localhost:8000/api/orders/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ver una orden específica:

```bash
curl -X GET "http://localhost:8000/api/orders/1" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 6. Interacciones (no requiere autenticación)

### Registrar una interacción (puede ser de usuarios anónimos o registrados):

```bash
curl -X POST "http://localhost:8000/api/interacciones/" \
     -H "Content-Type: application/json" \
     -d '{
           "product_id": 1,
           "interaction_type": "view",
           "interaction_metadata": "Usuario vio el producto en la página principal"
         }'
```

Para usuarios autenticados, se asociará automáticamente el user_id. Para usuarios anónimos, se registrará la dirección IP.

### Registrar una interacción con token (para usuarios autenticados):

```bash
curl -X POST "http://localhost:8000/api/interacciones/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
           "product_id": 1,
           "interaction_type": "click",
           "interaction_metadata": "Usuario hizo clic en el botón de compra"
         }'
```

## Notas importantes:

1. Reemplaza `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` con el token real que recibes al iniciar sesión.
2. Los endpoints protegidos requieren autenticación mediante el token JWT.
3. Cada usuario solo puede acceder a su propio carrito y órdenes.
4. Solo los administradores pueden crear productos y ver todas las órdenes e interacciones.
5. Las interacciones pueden ser registradas por usuarios anónimos (se guarda su IP) o autenticados (se asocia a su cuenta).


## Event driven

https://docs.cloud.google.com/eventarc/docs/event-driven-architectures