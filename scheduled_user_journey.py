import random
import requests
import time
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import schedule

# Base URL for the API (connecting to the app service from inside the container)
BASE_URL = "http://localhost:8000"

PAYMENT_METHODS = [
    "credit_card", "debit_card", "paypal", "bank_transfer", 
    "cash_on_delivery", "digital_wallet"
]

BANKS = [
    "Visa", "MasterCard", "American Express", "Discover", 
    "Chase", "Wells Fargo", "Bank of America", "Citi"
]

USER_NAMES = ['Eleanor Vance', 'Marcus Thorne', 'Chloe Zhang', 'Sebastian Rossi',
       'Isabella Garcia', 'Kenji Tanaka', 'Olivia Chen', 'Elias Vogel',
       'Aisha Mensah', "Liam O'Connell", 'Zoe Papadopoulos',
       'Caleb Murphy', 'Maya Patel', 'Alexander Volkov', 'Sofia Silva',
       'Daniel Kim', 'Charlotte Dubois', 'Hugo Larsen', 'Emilia Nowak',
       'Noah Schmidt', 'Ava Ivanova', 'Leo Costa', 'Mia Fitzgerald',
       'Oliver Johansson', 'Luna Santos', 'Ethan Bennett',
       'Harper Wallace', 'Arthur Li', "Grace O'Brien", 'Henry Müller',
       'Lily Campbell', 'Jack Fischer', 'Stella Rivera',
       'Thomas Gallagher', 'Violet Kumar', 'Lucas Esposito',
       'Penelope Brooks', 'Mateo Hoffman', 'Scarlett Walsh',
       'David Nielsen', 'Aurora Gupta', 'Samuel Chavez', 'Riley Chen',
       'Julian MacDonald', 'Hazel Sato', 'Charles Bryant', 'Ellie Morgan',
       'Benjamin Reed', 'Nora Price', 'Jacob West', 'Zoe Freeman',
       'William Coleman', 'Clara Stephens', 'Michael Park',
       'Evelyn Snyder', 'Adam Tucker', 'Abigail Grant', 'Ryan Cheng',
       'Elizabeth Pierce', 'Nathan Dawson', 'Addison Barber',
       'Isaac Hawkins', 'Lillian Holland', 'John Patterson',
       'Anna Rhodes', 'Owen Jennings', 'Savannah Keller', 'Wyatt Wong',
       'Bella Warner', 'Luke Medina', 'Skylar Almeida', 'Jayden Silva',
       'Lucy Farrell', 'Dylan Boone', 'Paisley Lynch', 'Carter Curry',
       'Gianna Poole', 'Gabriel Sherman', 'Alexis Norton',
       'Joshua Caldwell', 'Aaliyah Thornton', 'Anthony Stokes',
       'Serenity Potter', 'Christopher Lambert', 'Kennedy Francis',
       'Joseph Tyler', 'Naomi Hines', 'Isaiah Byrd', 'Mary Gross',
       'Andrew Sharpe', 'Cora Warren', 'Jonathan Rose', 'Ariana Daniels',
       'Jeremiah Page', 'Elena Stanley', 'Robert Swanson',
       'Melanie Payne', 'Nicholas Ballard', 'Lydia Hudson',
       'Christian Moss', 'Brianna Rivera', 'Landon Black', 'Taylor Myers',
       'Aaron Ford', 'Sophie Hamilton', 'Eli Graham', 'Ashley Woods',
       'Hunter Cole', 'Maria West', 'Connor Jordan', 'Ruby Owens',
       'Cameron Reynolds', 'Leah Fisher', 'Adrian Ellis',
       'Madeline Harrison', 'Austin Gibson', 'Katherine Mcdonald',
       'Jordan Cruz', 'Allison Marshall', 'Dominic Reeves',
       'Vivian Burgess', 'Brandon Henderson', 'Hadley Lawson',
       'Tyler Sims', 'Jasmine Fowler', 'Jose Sanders', 'Morgan Watts',
       'Zachary Hunter', 'London Gomez', 'Kevin Murray', 'Ximena Dunn',
       'Gavin Perkins', 'Andrea Villa', 'Ayden Romero', 'Nicole Keller',
       'Logan Todd', 'Valentina Chambers', 'Ian Larson', 'Brooke Hoffman',
       'Mason Manning', 'Paige Nguyen', 'Evan Rhodes', 'Faith Silva',
       'Chase Bowers', 'Trinity Buchanan', 'Jason Moran',
       'Julia Roberson', 'Parker Blake', 'Rylee Joseph', 'Xavier Wilkins',
       'Alexa Newton', 'Bentley Higgins', 'Margaret Clayton',
       'Nolan Stokes', 'Isabel Maxwell', 'Blake Doyle', 'Emery Ward',
       'Colton French', 'Adeline Hale', 'Angel Leonard',
       'Josephine Bridges', 'Cooper Horton', 'Sara Barrett',
       'Tristan Cummings', 'Amy Wilkerson', 'Damian Parsons',
       'Finley Dickson', 'Carlos Vaughan', 'Quinn Walters',
       'Justin Barker', 'Reagan Christensen', 'Jose Pittman',
       'Gabrielle Terry', 'Bryson Blair', 'Delilah Randolph',
       'Weston Moon', 'Daisy Michael', 'Silas Logan', 'Athena Haynes',
       'Maxwell Short', 'Lyla Powers', 'Juan Russo', 'Katie Brennan',
       'Cole Mcgee', 'Eliza Ashley', 'Miles Duke', "Alaina O'Neal",
       'Leonardo Bauer', 'Sienna Hoover', 'Sawyer Carr', 'Laura Molina',
       'Richard Erickson', 'Cecilia Fletcher', 'Declan Mckinney',
       'Genevieve Sharp', 'Braxton Solis', 'Lydia Macias', 'Micah Koch',
       'Harmony Flowers', 'Giovanni Rojas', 'Rose Norton', 'Eric Suarez',
       'Maddison Little', 'Kaleb Mclean', 'Jennifer Livingston',
       'Ashton Dudley', 'Brooklyn Hartman', 'Ryder Townsend',
       'Juliana Hardy', 'Nathaniel Savage', 'Lilly Dennis',
       'Vincent Mcguire', 'Maryam Daugherty', 'Jesse Travis',
       'Melissa Bender', 'Victor Mahoney', 'Destiny Valdez', 'Joel Levy',
       'Rachel Hodge', 'Edward Russo', 'Teagan Chan', 'King Stuart',
       'Lila May', 'Ivan Hull', 'Daniela Fry', 'Rowan Sheppard',
       'Angelina Crosby', 'George Klein', 'Paige Benjamin', 'Marcus Snow',
       'Eva Warner', 'Antonio Shepherd', 'Stephanie Jacobs',
       'Emmett Norris', 'Georgia Walton', 'Kayden Aguilar',
       'Arianna Wise', 'Bennett Davila', 'Ashlyn Snider',
       'Timothee Acosta', 'Fiona Booker', 'Bryan Novak', 'Jessica Carey',
       'Kaden Prince', 'Daisy Walls', 'Axel Zhang', 'Haley Anthony',
       'Calvin Whitney', 'Nina Underwood', 'Grant Baxter', 'Lauren Morse',
       'Preston Proctor', 'Alice Villegas', 'Luis Castillo',
       'Sophie Hull', 'Zane Lucero', 'Kate Maddox', 'Cash Tanner',
       'Miriam Krueger', 'Paul Glass', 'Ana Moss', 'Gage Glenn',
       'Elise Cline', 'Kenneth Delacruz', 'Gracie Camacho',
       'Malachi Dillon', 'Joanna Montes', 'Maximus Patton', 'Phoenix Yu',
       'Simon Mayer', 'Eleanor Conway', 'Jameson Lynn', 'Allison Adkins',
       'Alan Costa', 'Giselle Gates', 'Everett Pham', 'Molly Ray',
       'Chance Sosa', 'Faith Schmitt', 'Brooks Irwin',
       'Sarah Blankenship', 'Walker Cherry', 'Jade Mcdowell', 'Jude Wolf',
       'Trinity Chaney', 'Milo Kaufman', 'Rebecca Buck', 'Mark Lindsey',
       'Valerie Hancock', 'Felix Bray', 'Ada Middleton', 'Roberto Weiss',
       'Bianca Stark', "Amari O'Connor", 'Cassandra Duffy',
       'Shane Phelps', 'Heidi Melton', 'Caden Rosa', 'Sabrina Harrell',
       'Andre Conrad', 'Yaretzi Galvan', 'Tucker Jefferson',
       'Annalise Wade', 'Felix Bonilla', 'Juliette Michael', 'Derek Roth',
       'Kayla Singh', 'Bradley McMahon', 'Angelica Landry',
       'Colby Compton', 'Frida Cooley', 'Pedro Figueroa', 'Dahlia Simon',
       'Elliott Todd', 'Helena Whitney', 'Francisco Clarke',
       'Kamila Stanley', 'Dalton Zuniga', 'Lucia Sampson',
       'Remington Hooper', 'April Barron', 'Seth Brandt', 'Ember Malone',
       'Martin Donnell', 'Lindsey Kirby', 'Rhett Wilkinson',
       'Jordan Finley', 'Jaden Sellers', 'Carmen Bartlett',
       'Collin Atkinson', 'Jane Marquez', 'Corey Maddox',
       'Rosemary Boyle', 'Zion Law', 'Juliet Ponce', 'Clay Knapp',
       'Magnolia Cordova', 'Marcus Tapia', 'Melody Brandt', 'Jonah Huynh',
       'Michaela Key', 'Harvey Frye', 'Guadalupe Rivas', 'Neil Choi',
       'Elle Schmitt', 'Dillon Greene', 'Alyson Leon', 'Ricardo Kramer',
       'Lena Velazquez', 'Fernando Leblanc', 'Adriana Dougherty',
       'Drake Heath', 'June Clayton', 'Damon Byrd', 'Kelly Stuart',
       'Troy Mcintosh', 'Aniyah Hinton', 'Keith Krause', 'Cassidy Lynn',
       'Tony Braun', 'Miranda Sweeney', 'Ronnie Olsen', 'Bridget Shepard',
       'Johnny Gallagher', 'Angelique Frost', 'Julius Bond',
       'Kiara Monroe', 'Aryan Wolf', 'Harley Bernard', 'Russell Willis',
       'Tessa Molina', 'Corey Carlson', 'Daniella Avery',
       'Jamison Patrick', 'Lola Hubbard', 'Warren Norman', 'Amaya Parks',
       'Jeffrey Bradshaw', 'Carmen Cochran', 'Hassan Bauer',
       'Jocelyn Phelps', 'Frederick Holden', 'Mariana Russo',
       'Brock Wiley', 'Beatrice Ali', 'Enzo Vargas', 'Hope Farrell',
       'Kyler Petersen', 'Vivienne Huerta', 'Lane Randall', 'Elise Villa',
       'Raymond Tate', 'Lilah Benton', 'Landen Clayton', 'Nyla Singh',
       'Casey Chase', 'Daniela Morrow', 'Fabian Mahoney', 'Alicia Fritz',
       'Reese Dorsey', 'Helena Sosa', 'Arthur McCarty', 'Gwendolyn Roth',
       'Sergio Blackburn', 'Willa Pennington', 'Trent Wong', 'Joy Carey',
       'Bryan Haley', 'Lara Hancock', 'Louis Giles', 'Kassidy Short',
       'Ali Connell', 'Annie Stuart', 'Maurice Clayton',
       'Janiyah Farrell', 'Donald Andersen', 'Brynn Schmitt',
       'Iker Hoover', 'Erin Maynard', 'Theodore Hanna', 'Tatum Blackburn',
       'Edgar Boyle', 'Angel Mcmillan']

DOMAINS = [
  "aol.com",
  "att.net",
  "comcast.net",
  "facebook.com",
  "gmail.com",
  "gmx.com",
  "googlemail.com",
  "google.com",
  "hotmail.com",
  "hotmail.co.uk",
  "mac.com",
  "me.com",
  "mail.com",
  "msn.com",
  "live.com",
  "sbcglobal.net",
  "verizon.net",
  "yahoo.com",
  "yahoo.co.uk",
  "email.com",
  "fastmail.fm",
  "games.com",
  "gmx.net",
  "hush.com",
  "hushmail.com",
  "icloud.com",
  "iname.com",
  "inbox.com",
  "lavabit.com",
  "love.com",
  "outlook.com",
  "pobox.com",
  "protonmail.ch",
  "protonmail.com",
  "tutanota.de",
  "tutanota.com",
  "tutamail.com",
  "tuta.io",
  "keemail.me",
  "rocketmail.com",
  "safe-mail.net",
  "wow.com",
  "ygm.com",
  "ymail.com",
  "zoho.com",
  "yandex.com",
  "bellsouth.net",
  "charter.net",
  "cox.net",
  "earthlink.net",
  "juno.com",
  "btinternet.com",
  "virginmedia.com",
  "blueyonder.co.uk",
  "freeserve.co.uk",
  "live.co.uk",
  "ntlworld.com",
  "o2.co.uk",
  "orange.net",
  "sky.com",
  "talktalk.co.uk",
  "tiscali.co.uk",
  "virgin.net",
  "wanadoo.co.uk",
  "bt.com",
  "sina.com",
  "sina.cn",
  "qq.com",
  "naver.com",
  "hanmail.net",
  "daum.net",
  "nate.com",
  "yahoo.co.jp",
  "yahoo.co.kr",
  "yahoo.co.id",
  "yahoo.co.in",
  "yahoo.com.sg",
  "yahoo.com.ph",
  "163.com",
  "yeah.net",
  "126.com",
  "21cn.com",
  "aliyun.com",
  "foxmail.com",
  "hotmail.fr",
  "live.fr",
  "laposte.net",
  "yahoo.fr",
  "wanadoo.fr",
  "orange.fr",
  "gmx.fr",
  "sfr.fr",
  "neuf.fr",
  "free.fr",
  "gmx.de",
  "hotmail.de",
  "live.de",
  "online.de",
  "t-online.de",
  "web.de",
  "yahoo.de",
  "libero.it",
  "virgilio.it",
  "hotmail.it",
  "aol.it",
  "tiscali.it",
  "alice.it",
  "live.it",
  "yahoo.it",
  "email.it",
  "tin.it",
  "poste.it",
  "teletu.it",
  "mail.ru",
  "rambler.ru",
  "yandex.ru",
  "ya.ru",
  "list.ru",
  "hotmail.be",
  "live.be",
  "skynet.be",
  "voo.be",
  "tvcablenet.be",
  "telenet.be",
  "hotmail.com.ar",
  "live.com.ar",
  "yahoo.com.ar",
  "fibertel.com.ar",
  "speedy.com.ar",
  "arnet.com.ar",
  "yahoo.com.mx",
  "live.com.mx",
  "hotmail.es",
  "hotmail.com.mx",
  "prodigy.net.mx",
  "yahoo.ca",
  "hotmail.ca",
  "bell.net",
  "shaw.ca",
  "sympatico.ca",
  "rogers.com",
  "yahoo.com.br",
  "hotmail.com.br",
  "outlook.com.br",
  "uol.com.br",
  "bol.com.br",
  "terra.com.br",
  "ig.com.br",
  "itelefonica.com.br",
  "r7.com",
  "zipmail.com.br",
  "globo.com",
  "globomail.com",
  "oi.com.br"
]


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

def get_or_create_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user account or return existing user if email is already registered"""
    user_data = {
        "username": username,
        "email": email,
        "password": password
        # "created_at":date
    }
    response = requests.post(f"{BASE_URL}/api/users/", json=user_data)
    if response.status_code == 201:
        return response.json()
    elif response.status_code == 404:
        return get_user_by_email(user_data["email"])
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

def get_all_products() -> List[Dict[str, Any]]:
    """Get all products from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/products/")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return []

def get_product(product_id: int) -> Dict[str, Any]:
    """Get a specific product from the API"""
    response = requests.get(f"{BASE_URL}/api/products/{product_id}")
    if response.status_code == 200:
        return response.json()
    return {}

def add_to_cart(product_id: int, quantity: int, token: str) -> Dict[str, Any]:
    """Add a product to the cart"""
    cart_data = {
        "product_id": product_id,
        "quantity": quantity
    }
    
    response = requests.post(
            f"{BASE_URL}/api/cart/", 
            json=cart_data,
            headers={"Authorization": f"Bearer {token}"})
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

def create_interaction(user_id: int|None, 
                       product_id: int, 
                       interaction_type: str,
                       interaction_metadata: str|None = None,
                       token: str|None = None) -> Dict[str, Any]: 
    """Create a user interaction"""
    interaction_data = {
        "user_id": user_id,
        "product_id": product_id,
        "interaction_type": interaction_type
    }
    if interaction_metadata:
        interaction_data["interaction_metadata"] = interaction_metadata
    
    if token:
        response = requests.post(
            f"{BASE_URL}/api/interactions/", 
            json=interaction_data,
            headers={"Authorization": f"Bearer {token}"})
    else:
        response = requests.post(f"{BASE_URL}/api/interactions/", 
        json=interaction_data)

    if response.status_code == 201:
        return response.json()
    return {}

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

def convert_username(x:str) -> str:
    return x.replace("'", '').lower().replace(' ', '.')

def simulate_user_journey():
    """Simulate a complete user journey"""
    print(
        f"\n=== Starting User Journey Simulation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # Get all products
    products = get_all_products()
    if not products:
        print("No products available. Exiting simulation.")
        return
    print(f"Found {len(products)} products")
    
    # Randomly decide if the visitor will create a new account 
    # or continue as visitor without creating an account
    
    is_visitor = random.choice([True, False])

    if is_visitor:
        username, email, password = None, None, None
        user_id = None
        token = None
        
        # This visitor wants to create a new account later in the journey, so we will create interactions 
        # 
        want_a_new_account = random.choice([True, False])
        if want_a_new_account:
            # Create a new account
            username = random.choice(USER_NAMES)
            email = convert_username(username) + "@" + random.choice(DOMAINS) # "@example.com"
            password = convert_username(username)
            
            # Create user or get existing user if email is already registered
            user = get_or_create_user(username, email, password)
            
            # Authenticate a user and get an access token
            auth_response = auth(email, password)
            token = auth_response["access_token"]

            if not user:
                print("Failed to create user. Exiting simulation.")
                return
                
            user_id = user["id"]
            print(f"Created new user: {user['username']} (ID: {user_id})")
        else:
            print("Continuing as visitor without creating an account")
        
    else:
        total_user = get_total_user()
        if total_user == 0:
            username = random.choice(USER_NAMES) # + str(random.randint(100, 999))
            email = convert_username(username) + "@" + random.choice(DOMAINS) # "@example.com"
            password = convert_username(username)
            
            # Create user or get existing user if email is already registered
            user = get_or_create_user(username, email, password)
            
            # Authenticate a user and get an access token
            auth_response = auth(email, password)
            token = auth_response["access_token"]

            if not user:
                print("Failed to create user. Exiting simulation.")
                return
            
        user_id = np.random.randint(0, total_user['Total'])
        user = get_user_by_id(user_id)
        
        auth_response = auth_without_password(user['email'])
        token = auth_response["access_token"]

        print(f"Using existing account (User ID: {user_id})")

    
    # Track user interactions
    interactions = []
    
    # Randomly decide how many products the user will view
    num_products_to_view = random.randint(3, 10)
    print(f"User will view {num_products_to_view} products")
    
    # Select random products to view
    viewed_products = random.sample(products, num_products_to_view) 
    # min(num_products_to_view, len(products)))

    products_in_basket = []
    
    # Simulate viewing products
    # For each product, we will randomly decide if the user will click on it,
    # add it to cart, or just view it and move on
    for product in viewed_products:
        # Record view interaction
        interaction = create_interaction(
            user_id=user_id, 
            product_id=product["id"], 
            interaction_type="view", 
            interaction_metadata=None,
            token=token)
        if interaction:
            interactions.append(interaction)
            print(f"User viewed product: {product['name']}")

        # Randomly decide if the user will try to add to cart
        if random.choice([True, False]):
            if not token:
                print("User is not authenticated, skipping add to cart")
                continue

            # Check if product is available
            if product["is_available"] and product["stock_quantity"] > 0:
                # Randomly decide quantity to add
                quantity = random.randint(1, min(3, product["stock_quantity"]))
                
                # Add to cart
                cart_item = add_to_cart(product["id"], quantity, token=token)
                if cart_item:
                    print(f"User added {quantity} x {product['name']} to cart")
                    
                    # Record add_to_cart interaction
                    interaction_metadata = f"quantity: {quantity}"
                    interaction = create_interaction(
                        user_id, product["id"], "add_to_cart", interaction_metadata, 
                        token=token)
                    if interaction:
                        interactions.append(interaction)
                    
                    # Add to purchased products list for potential checkout
                    products_in_basket.append({
                        "product_id": product["id"],
                        "quantity": quantity,
                        "product": product
                    })
                else:
                    print(f"Failed to add {product['name']} to cart")
            else:
                # Product is out of stock
                print(f"User tried to add {product['name']} to cart but it's out of stock")
                
                # Record out_of_stock interaction
                interaction = create_interaction(
                    user_id, product["id"], "out_of_stock", token=token)
                
                if interaction:
                    interactions.append(interaction)
                
                # Simulate restocking process
                print(f"Triggering restock for {product['name']}")
                new_stock = random.randint(5, 20)
                updated_product = update_product_stock(product["id"], new_stock)
                if updated_product:
                    print(f"Restocked {product['name']} with {new_stock} units")
        
        # Random delay to simulate real browsing
        time.sleep(random.uniform(0.5, 2.0))
    
    # Randomly decide if the user will make a purchase
    if products_in_basket and random.choice([True, False, True]):  # 66% chance to purchase
        print(f"User is proceeding to checkout with {len(products_in_basket)} items")
        if not token:
            print("User is not authenticated, skipping purchase")
            return
        
        # Prepare order items
        order_items = [
            {"product_id": item["product_id"], "quantity": item["quantity"]} 
            for item in products_in_basket
        ]
        
        # Select random payment method and bank
        payment_method = random.choice(PAYMENT_METHODS)
        bank = random.choice(BANKS)
        
        # Create order
        order = create_order(order_items, payment_method, bank, token)
        if order:
            print(f"Order created successfully (ID: {order['id']})")
            print(f"Total amount: ${order['total_amount']:.2f}")
            print(f"Payment method: {payment_method} ({bank})")
            
            # Record purchase interaction
            for item in products_in_basket:
                interaction_metadata = f"order_id: {order['id']}, quantity: {item['quantity']}, total: {order['total_amount']:.2f}"
                interaction = create_interaction(
                    user_id, item["product_id"], "purchase", interaction_metadata,
                    token=token)
                if interaction:
                    interactions.append(interaction)
        else:
            print("Failed to create order")
    else:
        print("User did not proceed with purchase")
    
    print(f"=== User Journey Simulation Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Total interactions recorded: {len(interactions)}")

def run_scheduler():
    """Run the scheduler to execute the simulation every 3 minutes"""
    # Schedule the job every 3 minutes
    schedule.every(1).minutes.do(simulate_user_journey)
    
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