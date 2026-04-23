import random
import requests
import time
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import schedule
import json
import logging
from faker import Faker


# Fake data generator
fake = Faker()

# Base URL for the API (connecting to the app service from inside the container)
BASE_URL = "http://localhost:8000"

logging.basicConfig(
    filename='app.log', 
    filemode='a', # 'a' for append (default), 'w' to overwrite
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

PAYMENT_METHODS = {
    'Digital Wallets (E-wallets)': ['PayPal', 'Apple Pay', 'Google Pay',
                                    'Samsung Pay', 'Venmo', 'Alipay', 'WeChat Pay'],
    'Credit & Debit Cards': ['Visa', 'Mastercard', 'American Express', 'Discover', 'Diners Club'],
    'Buy Now, Pay Later (BNPL)': ['Klarna', 'Affirm', 'Afterpay', 'Sezzle', 'Zip'],
    'Bank Transfers / ACH': ['ACH (USA)', 'SEPA (Europe)', 'Faster Payments (UK)'],
    'Cryptocurrency': ['Bitcoin (BTC)', 'Ethereum (ETH)', 'USDT', 'USDC', 'Litecoin'],
    'Cash on Delivery (COD)': ['Traditional COD (very common in emerging markets)']}


STATES = ['start', 'landing_page', 'search', 'category_view', 'product_view', 
         # 'variant_selected', 
         'add_to_cart', 'cart_view', 'remove_from_cart', 'checkout_started', 
         'login_required', 'shipping_info', 'payment_info', 'purchase',
         # 'wishlist', 
         'exit']

# N_PRODUCTS = 10
DEFAULT_PASSWORD = "Password123!"

def normalize_row(row: np.ndarray) -> np.ndarray:
    total = row.sum()
    if total <= 0:
        raise ValueError("Row total must be > 0")
    return row / total

def read_matrix_transition_from_json(file_path: str) -> dict:
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Ensure the order of states is consistent with the STATES list
    matrix = {}
    for state in STATES:
        row = data.get(state, [0] * len(STATES))
        matrix[state] = normalize_row(np.asarray(row))
    
    return matrix
    
# Matrix transition 17x17
matrix_transition = read_matrix_transition_from_json('matrix_transition.json')


# ------------------- START IP -----------------------


def fetch_random_ip_address() -> Dict[str, Any]:
    """Get random IP from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/ip_address/", params={"limit": 1})
        if response.status_code == 200:
            response_01 =response.json()
            return response_01[0]
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict()

def register_ip_address(ip_address: str) -> Dict[str, Any]:
    """Create a new IP address or return existing IP if it already exists"""
    data = {"ip_address": ip_address}
    response = requests.post(f"{BASE_URL}/api/ip_address/", json=data)

    if response.status_code == 201:
        return response.json()
    return {}

def fetch_ip_address(id_address: str) -> Dict[str, Any]:
    """Get a data of an IP address from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/ip_address/{id_address}")
        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict()

# -------------------- END IP ------------------------

# ------------------- START USER -----------------------
def get_total_user() -> Dict[str, Any]:
    """Get all users from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/users/total")
        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict()
    
def get_user_by_id(idx) -> Dict[str, Any]:
    """Get a user by their ID from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/users/{idx}")
        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict()
    
def get_user_by_email(email: str) -> Dict[str, Any]:
    """Get a user by their email from the API"""

    try:
        response = requests.get(f"{BASE_URL}/api/users/email/{email}")
        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict()

def register_user(full_name:str, username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user account or return existing user if email is already registered"""
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name":full_name
    }
    response = requests.post(f"{BASE_URL}/api/users/", json=user_data)
    if response.status_code == 201:
        return response.json()
    return {}

def auth_without_password(email: str) -> Dict[str, Any]:
    """Authenticate a user and get an access token from the API"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/token_without_password", 
            json={"email": email})

        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict(
            access_token="",
            token_type="bearer"
        )

def auth(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user and get an access token from the API"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/token", 
            json={"email": email, "password": password})

        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict(
            access_token="",
            token_type="bearer"
        )

def register_ip_address_by_user(ip_address_id: int, user_id: int) -> Dict[str, Any]:
    """Register an IP address for a user"""
    ip_data = {
        "ip_address_id": ip_address_id,
        "user_id": user_id
    }
    response = requests.post(f"{BASE_URL}/api/user_ip_address/", json=ip_data)
    if response.status_code == 201:
        return response.json()
    return {}

def get_ip_address_user_by_ip_address_id(ip_address_id: int):
    """Check if the IP is used by an existing user"""
    response = requests.get(f"{BASE_URL}/api/user_ip_address/{ip_address_id}")
    if response.status_code == 200:
        return response.json()
    return {}

# -------------------- END USER -------------------------

# ------------------ START PRODUCT ----------------------
def get_n_random_products(n_products:int) -> set:
    """Get n random products from the API"""
    response = requests.get(f"{BASE_URL}/api/products/", params={"limit": n_products})
    if response.status_code == 200:
        results = response.json()
        return {result['id'] for result in results}
    return set()

def check_availability(product_id: int, quantity: int) -> bool:
    """Get n random products from the API"""
    response = requests.get(
        f"{BASE_URL}/api/products/", 
        params={"product_id": product_id, "quantity": quantity})
    if response.status_code == 200:
        # response.json()
        return True
    else:
        return False



def restock_product(product_id: int) -> Dict[str, Any]:
    """
    Restock a product by generating a random stock quantity between 5 and 20 units.
    
    Parameters:
    product_id (int): The ID of the product to restock.
    
    Returns:
    A dictionary containing the updated product information if the restock was successful, otherwise an empty dictionary.
    """
    new_stock = random.randint(5, 20)
    
    updated_product = update_product_stock(product_id, new_stock)
    
    if updated_product:
        return updated_product
    else:
        return {}
    # if updated_product:
    #     print(f"Restocked {product_id} with {new_stock} units")

def update_product_stock(product_id: int, new_stock: int) -> Dict[str, Any]:
    """Update product stock"""
    product_data = {
        "stock_quantity": new_stock,
        "is_available": new_stock > 0
    }
    response = requests.put(f"{BASE_URL}/api/products/{product_id}", json=product_data)
    if response.status_code == 200:
        return response.json()
    return {}
   
# ------------------ END PRODUCT ---------------------
def add_to_cart(product_id: int, quantity: int, ip_id: int) -> Dict[str, Any]:
    """Add a product to the cart"""
    cart_data = {
        "product_id": product_id,
        "quantity": quantity,
        "ip_id": ip_id
    }
    
    response = requests.post(
            f"{BASE_URL}/api/cart/", 
            json=cart_data)
    if response.status_code == 201:
        return response.json()
    return {}

def create_order(
    items: List[Dict[str, Any]], 
    payment_method: str, bank: str, token: str) -> Dict[str, Any]:
    """Create a new order"""
    order_data = {
        "items": items,
        "payment_method": payment_method,
        "bank": bank
    }
    
    response = requests.post(
            f"{BASE_URL}/api/orders/", 
            json=order_data,
            headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 201:
        return response.json()
    return {}

def create_interaction(ip_address_id: int,
                       interaction_type: str,
                       interaction_metadata: str|None = None
                       ) -> Dict[str, Any]:
    
    """Create a user interaction"""
    data = {
        "ip_address_id": ip_address_id,
        "interaction_type": interaction_type,
        "interaction_metadata":interaction_metadata
        }

    response = requests.post(f"{BASE_URL}/api/interactions/", json=data)

    if response.status_code == 201:
        return response.json()
    return {}


def simulate_user_journey():
    """Simulate a complete user journey"""
    print(
        f"\n=== Starting User Journey Simulation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
        )
    
    # 1. New connection
    
    is_new_device = np.random.choice(
        [True, False], p=[0.12, 0.88], replace=False)
    
    def generator_of_ip_address():
        ip_address = fake.unique.ipv4()
        db_ip_address = register_ip_address(ip_address)
        
        if db_ip_address:
            ip_address_id = db_ip_address['id']
        else:
            logging.error("Could not register ip address: {ip_address}")
            db_ip_address = fetch_ip_address(ip_address)
            logging.info("Fetched ip address: {db_ip_address}")

            if not db_ip_address:
                logging.error("Could not fetch ip address: {ip_address}")
                return {}
            ip_address_id = db_ip_address['id']

        return {'id': ip_address_id, 'ip_address':ip_address}
    
    def generator_of_user():
        # if the email is already registered, 
        # We will add this ip to the existing user with that email and login 
        # to that account instead of creating a new account 

        user_name = fake.unique.user_name()
        email = fake.unique.email()
        full_name = fake.unique.name()
        
        db_user = register_user(full_name, user_name, email, DEFAULT_PASSWORD)
        if db_user:
            return db_user
        return {}
        
    
    if is_new_device:
        db_ip_address = generator_of_ip_address()
        if not db_ip_address:
            return
        ip_address_id = db_ip_address['id']

    else:
        db_ip_address = fetch_random_ip_address()
        if not db_ip_address:
            logging.error("Could not fetch random ip address")
            return
        ip_address_id = db_ip_address['id']
        
    # Set number of interactions for this user journey (between 1 and 50)
    n_interactions = random.randint(1, 50)

    def trajectory(ip_address_id:int, state:str, n:int, 
                   data:dict, interactions:list):
        
        
        if  state == 'start':
            logging.info(f"Starting user journey at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        elif state == 'landing_page':
            logging.info(f"User is on the landing page at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            interaction = create_interaction(ip_address_id, state)
            # print("interaction", interaction, ip_address_id, state)
            if interaction:
                logging.info(f"Interaction on landing page created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                interactions.append(interaction)
            else:
                logging.error(f"Could not create interaction on landing page at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif state == 'search':
            logging.info(f"User is searching at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            n_products = random.randint(1, 8)
            results = get_n_random_products(n_products)
            # print("results", results)
            if results:
                additional_results = results.difference(data['results'])
                metadata = json.dumps(list(additional_results))
                if additional_results:
                    data['results'] = data['results'].union(additional_results)
                    interaction = create_interaction(ip_address_id, state, metadata)
                    if interaction:
                        interactions.append(interaction)
                    else:
                        logging.error(f"Could not create interaction on search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logging.info(f"No new results found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.error(f"Could not get random products at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
           
        elif state == 'category_view':
            logging.info(f"User is viewing a category at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            n_products = random.randint(1, 9)
            results = get_n_random_products(n_products)
            # print("results", results)
            if results:
                additional_results = results.difference(data['results'])
                metadata = json.dumps(list(additional_results))
                if additional_results:
                    data['results'] = data['results'].union(additional_results)
                    interaction = create_interaction(ip_address_id, state, metadata)
                    if interaction:
                        interactions.append(interaction)
                    else:
                        logging.error(f"Could not create interaction on category view at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logging.info(f"No new results found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.error(f"Could not get random products at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
        elif state == 'product_view':
            logging.info(f"User is viewing a product at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            n_products = random.randint(1, 5)
            n_results = len(data['results'])
            results = np.asarray(list(data['results']))
            
            if n_results > 0:
                # print("product_view results",results)
                # print(n_products)
                # print(n_results)
                # print(results)
                viewed = set(
                    np.random.choice(results, min(n_products, n_results), replace=False).tolist()
                    )
                additional_viewed = viewed.difference(data['viewed'])
                if additional_viewed:
                    metadata = json.dumps(list(additional_viewed))
                    data['viewed'] = data['viewed'].union(additional_viewed)
                    interaction = create_interaction(ip_address_id, state, metadata)
                    if interaction:
                        interactions.append(interaction)
                    else:
                        logging.error(f"Could not create interaction on product view at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                else:
                    logging.info(f"No new results found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.info(f"No new results found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        elif state == 'add_to_cart':
            logging.info(f"User is adding to cart at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            n_products = random.randint(1, 3)
            n_viewed = len(data['viewed'])
            viewed = np.asarray(list(data['viewed']))
            if n_viewed > 0:
                cart = set(
                    np.random.choice(viewed, min(n_products, n_viewed), replace=False).tolist()
                    )
                if data['cart']:
                    base_cart = set(data['cart'].keys())
                    additional_cart = cart.difference(base_cart)
                else:
                    additional_cart = cart
                    
                    
                if additional_cart:
                    additional_data = {}
                    restock_data = {}
                    for product_id in additional_cart:
                        quantity = random.randint(1, 2)
                        if check_availability(product_id, quantity):
                            additional_data[product_id] = {'quantity': quantity}
                            logging.info(f"Added {product_id} to cart with {quantity} units")
                            # data['viewed'].discard(product_id)
                        else:
                            logging.error(f"Could not add {product_id} to cart, out of stock, at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            updated_product = restock_product(product_id)
                            if updated_product:
                                restock_data[product_id] = {'quantity': quantity}
                                logging.info(f"Restocked {product_id} with {quantity} units")
                            else:
                                logging.error(f"Could not restock {product_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # print(additional_data)
                    data['cart'].update(additional_data)
                    metadata = json.dumps(additional_data)
                    restock_metadata = json.dumps(restock_data)
                    interaction_restock = create_interaction(ip_address_id, 'restock', restock_metadata)
                    if interaction_restock:
                        logging.info(f"Interaction on restock created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        interactions.append(interaction_restock)
                    else:
                        logging.error(f"Could not create interaction on restock at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                        
                    interaction = create_interaction(ip_address_id, state, metadata)
                    if interaction:
                        logging.info(f"Interaction on add to cart created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        interactions.append(interaction)
                    else:
                        logging.error(f"Could not create interaction on add to cart at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                        logging.info(f"No new results found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.error(f"No products in viewed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif state == 'cart_view':
            logging.info(f"User is viewing cart at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            interaction = create_interaction(ip_address_id, state)        
            if interaction:
                logging.info(f"Interaction on cart view created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                interactions.append(interaction)
            else:
                logging.error(f"Could not create interaction on cart view at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif state == 'remove_from_cart':
            logging.info(f"User is removing from cart at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if data['cart']:
                base_cart = np.asarray(data['cart'].keys())
                # base_cart = np.asarray(base_cart)
                remove = np.random.choice(base_cart, 1, replace=False)
                remove = remove[0]
                
                data['remove'] = data['remove'].join({remove})
                data['cart'].pop(remove)
                metadata = json.dumps([remove])
                interaction = create_interaction(ip_address_id, state, metadata)    
                if interaction:
                    logging.info(f"Interaction on remove from cart created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    interactions.append(interaction)
                else:
                    logging.error(f"Could not create interaction on remove from cart at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.error(f"No products in cart at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif state == 'checkout_started':
            logging.info(f"User is checking out at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if data['order']:
                logging.info(f"Order already created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                pass
            else:
                data['order'] = {'status':{'payment':False, 'logging':False, 'shipping':None, 'token':None},
                                'items':None}
                # Create order
                interaction = create_interaction(ip_address_id, state)    
                if interaction:
                    logging.info(f"Interaction on checkout started created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    interactions.append(interaction)
                else:
                    logging.error(f"Could not create interaction on checkout started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif state == 'login_required':
            # Create user and login
            logging.info(f"User is logging in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if not data['order']['status']['logging']:
                logging.info(f"User is logging in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                if is_new_device:
                    logging.info(f"User is new device logging in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    db_user = generator_of_user()
                    if db_user:
                        user_id = db_user['id']
                        email = db_user['email']
                        db_ip_address_by_user = register_ip_address_by_user(ip_address_id, user_id)
                        
                        if db_ip_address_by_user:
                            auth_response = auth(email, DEFAULT_PASSWORD)
                            if auth_response:
                                data['order']['status']['logging'] = True
                                data['order']['status']['token'] = auth_response["access_token"]
                                interaction = create_interaction(ip_address_id, state, 'success')    
                                if interaction:
                                    logging.info(f"Interaction on login success created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                    interactions.append(interaction)
                                else:
                                    logging.error(f"Could not create interaction on login success at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                            else:
                                logging.error(f"Could not login user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            logging.info(f"Could not register ip address by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        logging.error(f"Could not create user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                else:
                    logging.info(f"User is not new device logging in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    ip_address_user = get_ip_address_user_by_ip_address_id(ip_address_id)
                    
                    # We need to check if this IP is already associated with an existing user, if not we will 
                    # create a new account for that user and add this IP to that account. 
                    # If yes, we will login to that account.
                    if not ip_address_user:
                        logging.info("User does not have IP address associated with them at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        db_user = generator_of_user()
                        if db_user:
                            user_id = db_user['id']
                            email = db_user['email']
                            db_ip_address_by_user = register_ip_address_by_user(ip_address_id, user_id)
                            if db_ip_address_by_user:
                                auth_response = auth(email, DEFAULT_PASSWORD)
                                if auth_response:
                                    data['order']['status']['logging'] = True
                                    data['order']['status']['token'] = auth_response["access_token"]
                                    interaction = create_interaction(ip_address_id, state, 'success')
                                    if interaction:
                                        interactions.append(interaction)
                                    else:
                                        logging.error(f"Could not create interaction on login success at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                else:
                                    logging.error(f"Could not login user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            else:
                                logging.error(f"Could not register ip address by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                    else:
                        logging.info("User has IP address associated with them at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        user = get_user_by_id(ip_address_user['user_id'])
                        auth_response = auth_without_password(user['email'])
                        if auth_response:
                            data['order']['status']['logging'] = True
                            data['order']['status']['token'] = auth_response["access_token"]
                            interaction = create_interaction(ip_address_id, state, 'success')
                            if interaction:
                                interactions.append(interaction)
                            else:
                                logging.error(f"Could not create interaction on login success at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            logging.info(f"Could not login user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                interaction = create_interaction(ip_address_id, state, 'fail')
                if interaction:
                    logging.info(f"Interaction on login_required created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    interactions.append(interaction)
                else:
                    logging.error(f"Could not create interaction on login_required at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.error(f"User is already logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif state == 'shipping_info':
            logging.info(f"User is shipping info at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if not data['order']['status']['shipping']:
                address = fake.unique.address()
                data['order']['status']['shipping'] = address
                metadata = json.dumps([address])
                interaction = create_interaction(ip_address_id, state, metadata)
                    
                if interaction:
                    logging.info(f"Interaction on shipping_info created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    interactions.append(interaction)
                else:
                    logging.error(f"Could not create interaction on shipping_info at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logging.info(f"User already has shipping info at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif state == 'payment_info':
            logging.info(f"User is payment info at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if not data['order']['status']['payment']:
                status_payment = np.random.choice([True, False], p=[0.8, 0.2], replace=False)
                
                if status_payment:
                    logging.info(f"User had changed payment info to True at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    data['order']['status']['payment'] = True
                
                metadata = json.dumps({'payment':1 if status_payment else 0})
                interaction = create_interaction(ip_address_id, state, metadata)
                    
                if interaction:
                    logging.info(f"Interaction on payment_info created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    interactions.append(interaction)
            else:
                logging.info(f"User already has payment info at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif state == 'purchase':
            logging.info(f"User is purchase at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if (
                (data['order']['status']['payment'] and data['order']['status']['shipping']) and 
                (data['order']['status']['logging'] and data['order']['status']['token'])
                ):

                data['order']['items'] = data['cart'].copy()
                
                data['cart'].clear()

                payment_method = np.random.choice(list(PAYMENT_METHODS.keys()))
                bank = np.random.choice(PAYMENT_METHODS[payment_method])
                
                # 2. Get token
                # Prepare order items
                order_items = [
                    {"product_id": item["product_id"], "quantity": item["quantity"]} 
                    for item in data['order']['items'].values()
                ]
                
                # 4. Create order with all products in the cart

                order = create_order(order_items, payment_method, bank, data['order']['status']['token'])

                if order:
                    logging.info(f"Order created successfully (ID: {order['id']}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    # print(f"Order created successfully (ID: {order['id']})")
                    # print(f"Total amount: ${order['total_amount']:.2f}")
                    # print(f"Payment method: {payment_method} ({bank})")
                    
                    # 6. Create interactions for all products in the order
                    metadata = json.dumps(data['order']['items'])
                    interaction = create_interaction(ip_address_id, state, metadata)
                    # interaction = create_interaction(ip_address_id, state, json.dumps(data['order']['items']))
                    if interaction:
                        logging.info(f"Interaction on purchase created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")    
                        interactions.append(interaction)
                    else:
                        logging.error(f"Could not create interaction on purchase at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:

                    logging.error(f"Could not create order at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    metadata = json.dumps(data['order']['items'])
                    interaction = create_interaction(ip_address_id, state, metadata)
                            
                    # interaction = create_interaction(ip_address_id, state, json.dumps(order))
                    if interaction:
                        logging.info(f"Interaction on purchase created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")    
                        interactions.append(interaction)
                    else:
                        logging.error(f"Could not create interaction on purchase at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                n = 1
            else:
                logging.error(f"User have not purchased in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
        elif state == 'exit':
            logging.info(f"User is exiting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            interaction = create_interaction(ip_address_id, state)
                    
            if interaction:
                logging.info(f"Interaction on exit created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                interactions.append(interaction)
            else:
                logging.error(f"Could not create interaction on exit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            n = 1
        else:
            raise ValueError("State not found")

        # interactions.append(10)
        # create interaction
        if n <= 1:
            return data, interactions
        
        n-=1
            # idx = STATES.index(state)
        prob = matrix_transition[state].copy()
        next_state = np.random.choice(STATES, p=prob, replace=False)
        print("Next state:", next_state)
        return trajectory(ip_address_id, next_state, n, data, interactions)
        
    data = {'results': set(), 'viewed': set(), 'cart': {}, 'remove': set(), 'order': {}}
    interactions = []
    
    data, interactions = trajectory(
        ip_address_id, 'start', n_interactions, data, interactions)
    
    # Select
    # Save
    # Add card
    
    print(f"=== User Journey Simulation Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Total interactions recorded: {len(interactions)}")

def run_scheduler():
    """Run the scheduler to execute the simulation every 3 minutes"""
    # Schedule the job every 3 minutes
    schedule.every(5).seconds.do(simulate_user_journey)
    
    # Run the scheduler
    print("Scheduler started. Running user journey simulation every 3 minutes...")
    print("Press Ctrl+C to stop the scheduler.")
    
    # Run the first simulation immediately
    simulate_user_journey()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Run the scheduler
    run_scheduler()
    # simulate_user_journey()