import random
import requests
import time
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import schedule
import ipaddress
from uuid import uuid4
# from scheduled_user_journey import PAYMENT_METHODS


# Base URL for the API (connecting to the app service from inside the container)
BASE_URL = "http://localhost:8000"

payment_methods = {
    'Digital Wallets (E-wallets)': ['PayPal', 'Apple Pay', 'Google Pay',
  'Samsung Pay',
  'Venmo',
  'Alipay',
  'WeChat Pay'],
 'Credit & Debit Cards': ['Visa',
  'Mastercard',
  'American Express',
  'Discover',
  'Diners Club'],
 'Buy Now, Pay Later (BNPL)': ['Klarna',
  'Affirm',
  'Afterpay',
  'Sezzle',
  'Zip'],
 'Bank Transfers / ACH': ['ACH (USA)',
  'SEPA (Europe)',
  'Faster Payments (UK)'],
 'Cryptocurrency': ['Bitcoin (BTC)',
  'Ethereum (ETH)',
  'USDT',
  'USDC',
  'Litecoin'],
 'Cash on Delivery (COD)': ['Traditional COD (very common in emerging markets)']}

tasks = ['Select', 'Save', 'Add Cart', 'Remove', 'Order']
    
transition = np.asarray([
        [0.8 , 1.  , 0.88, 0.5 , 1.  ],
        [0.08, 0.  , 0.05, 0.  , 0.  ],
        [0.12, 0.  , 0.  , 0.  , 0.  ],
        [0.  , 0.  , 0.  , 0.  , 0.  ],
        [0.  , 0.  , 0.07, 0.5 , 0.  ]]
        )

names = ['Eleanor Vance', 'Marcus Thorne', 'Chloe Zhang', 'Sebastian Rossi',
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

domains = [
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

# ------------------- START IP -----------------------

def generate_ip_address() -> str:
    """
    That function can generate a total of 4,294,967,296 unique IP addresses
    """
    # Generates a random 32-bit integer and converts it to an IP string
    random_ip = ipaddress.IPv4Address(random.getrandbits(32))
    # response = {"ip":str(random_ip)}
    return str(random_ip)

def get_random_ip_address() -> Dict[str, Any]:
    """Get random IP from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/ip/random")
        if response.status_code == 200:
            return response.json()
        return dict()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Make sure the service is running.")
        return dict()

def create_ip_address(ip: str) -> Dict[str, Any]:
    """Create a new IP address or return existing IP if it already exists"""
    ip_data = {
        "ip": ip
    }
    response = requests.post(f"{BASE_URL}/api/ip/", json=ip_data)
    if response.status_code == 201:
        return response.json()
    return {}

def get_ip_address_by_ip_address(ip: str) -> Dict[str, Any]:
    """Get a data of an IP address from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/ip/{ip}")
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

def register_ip_address_by_user(ip_address_id: int, user_id: int) -> Dict[str, Any]:
    """Register an IP address for a user"""
    ip_data = {
        "ip_id": ip_address_id,
        "user_id": user_id
    }
    response = requests.post(f"{BASE_URL}/api/ips_users/", json=ip_data)
    if response.status_code == 201:
        return response.json()
    return {}

def create_user(username: str, email: str, password: str) -> Dict[str, Any]:
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
    # elif response.status_code == 404:
    #     return get_user_by_email(user_data["email"])
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

# -------------------- END USER -------------------------

# ------------------ START PRODUCT ---------------------
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

def get_product() -> Dict[str, Any]:
    """Get a random product from the API"""
    response = requests.get(f"{BASE_URL}/api/products/random")
    if response.status_code == 200:
        return response.json()
    return {}

def check_product_availability(product: dict):
    if product["is_available"] and product["stock_quantity"] > 0:
        return True
    else:
        return False

def check_ip_is_used_by_user(ip_address_id: str):
    """Check if the IP is used by an existing user"""
    response = requests.get(f"{BASE_URL}/api/ips_users/{ip_address_id}")
    if response.status_code == 200:
        return True
    return False

def get_ip_address_user_by_ip_address_id(ip_address_id: int):
    """Check if the IP is used by an existing user"""
    response = requests.get(f"{BASE_URL}/api/ips_users/{ip_address_id}")
    if response.status_code == 200:
        return response.json()
    return {}

def get_user_by_ip_address(ip_address: str) -> Dict[str, Any]:
    """Get a user by their IP address from the API"""
    response = requests.get(f"{BASE_URL}/api/ips_users/user/{ip_address}")
    if response.status_code == 200:
        return response.json()
    return {}

def restock_product(product: dict):
        # Product is out of stock
    print(f"User tried to add {product['name']} to cart but it's out of stock")
        
    # Simulate restocking process
    print(f"Triggering restock for {product['name']}")
    new_stock = random.randint(5, 20)
    updated_product = update_product_stock(product["id"], new_stock)
    if updated_product:
            print(f"Restocked {product['name']} with {new_stock} units")

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

def create_interaction(ip: str,
                       product_id: int,
                       interaction_type: str,
                       token: str|None = None
                       ) -> Dict[str, Any]:
    
    """Create a user interaction"""
    interaction_data = {
        "ip": ip,
        "product_id": product_id,
        "interaction_type": interaction_type
    }

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
    
    # response = requests.post(
    #         f"{BASE_URL}/api/interactions/", json=interaction_data)

def convert_username(x:str) -> str:
    return x.replace("'", '').lower().replace(' ', '.')

def simulate_user_journey():
    """Simulate a complete user journey"""
    print(
        f"\n=== Starting User Journey Simulation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
        )
    
    # 1. New connection
    
    is_new_device = np.random.choice(
        [True, False], p=[0.12, 0.88], replace=False)
    
    def complete_generator_of_ip_address():
        ip = generate_ip_address()
        db_created_ip = create_ip_address(ip)
        if db_created_ip:
            ip_address_id = db_created_ip['id']
        else:
            db_ip = get_ip_address_by_ip_address(ip)
            ip_address_id = db_ip['id']

        return {'id': ip_address_id, 'ip':ip}
    
    if is_new_device:
        ip_data = complete_generator_of_ip_address()
        ip = ip_data['ip']
        ip_address_id = ip_data['id']

    else:
        db_ip = get_random_ip_address()
        if not db_ip:
            ip_data = complete_generator_of_ip_address()
            ip = ip_data['ip']
            ip_address_id = ip_data['id']
        else:
            ip = db_ip['ip']
            ip_address_id = db_ip['id']
        
    # Set number of interactions for this user journey (between 1 and 50)
    n_interactions = random.randint(1, 50)
    

    def trajectory(task:str, n:int, 
                   data:dict, interactions:list):
        
        # ['Select', 'Save', 'Add Cart', 'Remove', 'Order']
        if task == 'Select':
            db_product = get_product()
            if db_product:
                data['Select'].append(db_product)
                interaction = create_interaction(ip_address_id, db_product['id'], 'Select')
        
        elif task == 'Save':
            db_product = data['Select'][-1]
            if check_product_availability(db_product):
                data['Save'].append(db_product)
                interaction = create_interaction(ip_address_id, db_product['id'], 'Save')
                # create_interaction()
            else:
                interaction = create_interaction(ip_address_id, db_product['id'], 'Out of stock')
                # Fill with the IP of seller or warehouse instead of the IP of the user
                updated_product = restock_product(db_product)
                if updated_product:
                    interaction = create_interaction(ip_address_id, db_product['id'], 'Restock')
                # create_interaction()
           
        elif task == 'Add Cart':
            db_product = data['Select'][-1]
            if check_product_availability(db_product):
                data['Add Cart'].append(db_product)
                
                interaction = create_interaction(ip_address_id, db_product['id'], 'Add Cart')
                # create_interaction()
                
            else:
                interaction = create_interaction(ip_address_id, db_product['id'], 'Out of stock')
                updated_product = restock_product(db_product)
                if updated_product:
                    interaction = create_interaction(ip_address_id, db_product['id'], 'Restock')
                # create_interaction()
            
        elif task == 'Remove':
            if data['Add Cart']:
                db_product = np.random.choice(data['Add Cart'])
                data['Select'].remove(db_product)
                data['Add Cart'].remove(db_product)
                data['Remove'].append(db_product)
                interaction = create_interaction(ip_address_id, db_product['id'], 'Remove')
                # create_interaction()
        elif task == 'Order':
            # 1. Add method of payment and bank
            payment_method = np.random.choice(list(payment_methods.keys()))
            bank = np.random.choice(payment_methods[payment_method])

            # 2. Add address
            # address = '123 Main St, Anytown, USA'

            # 3. Add an account if the user is a visitor and wants to create an account at this stage
            
            # if IP is related to an existing user We will login to that account.
            # otherwise we will create a new account for that user
            
            # If is a new device, we will create a new account for that user and add this IP to that account.
            
            if is_new_device:
                # Generate a random username and email for the new user

                # If the username or email is already registered, we will add this ip to the existing user with that username or email and login to that account instead of creating a new account

                pass
            
            else:
                ip_address_user = get_ip_address_user_by_ip_address_id(ip_address_id)
                
                # We need to check if this IP is already associated with an existing user, if not we will create a new account for that user and add this IP to that account. If yes, we will login to that account.
                if not ip_address_user:
                    name = random.choice(names)
                    random_number = random.randint(100, 999)
                    username = convert_username(name) + '.' + str(random_number)
                    domain = random.choice(domains)
                    email = username + "@" + domain

                    password = uuid4().hex[:8]
                    # if the email is already registered, 
                    # We will add this ip to the existing user with that email and login to that account instead of creating a new account 
                    user = create_user(username, email, password)
                    if not user:
                        user = get_user_by_email(email)
                        user_id = user['id']
                        ip_address_by_user = register_ip_address_by_user(ip_address_id, user_id)
                        if not ip_address_by_user:
                            pass

                        auth_response = auth_without_password(user['email'])
                        # print("Failed to create user. Exiting simulation.")
                        # return
                    else:
                        user_id = user['id']
                        ip_address_by_user = register_ip_address_by_user(ip_address_id, user_id)
                        auth_response = auth(email, password)
            
                else:
                    # This IP is already associated with an existing user, so we will continue as a visitor without creating an account
                    # ip_address_id = ip_address_user['ip_id'] 
                    # user_id = ip_address_user['user_id'] 
                    # ip_address_by_user = register_ip_address_by_user(
                    #     ip_address_user['ip_id'] , ip_address_user['user_id'] )
                    user = get_user_by_ip(ip_address_id)
                    auth_response = auth_without_password(user['email'])
                    pass

            token = auth_response["access_token"]

            # Prepare order items
            order_items = [
                {"product_id": item["product_id"], "quantity": item["quantity"]} 
                for item in data['Add Cart']
            ]
            
            # 4. Create order with all products in the cart

            order = create_order(order_items, payment_method, bank, token)

            if order:
                print(f"Order created successfully (ID: {order['id']})")
                print(f"Total amount: ${order['total_amount']:.2f}")
                print(f"Payment method: {payment_method} ({bank})")
                
                # 6. Create interactions for all products in the order
                for item in data['Add Cart']:
                    # interaction_metadata = f"order_id: {order['id']}, quantity: {item['quantity']}, total: {order['total_amount']:.2f}"
                    interaction = create_interaction(
                        ip_address_id, item["product_id"], "Purchase",
                        token=token)
                    if interaction:
                        interactions.append(interaction)
            else:
                print("Failed to create order")
            # 5. Update stock of products in the order

            

            # 7. Send an email confirmation (we can simulate this by creating an interaction of type "email_confirmation_sent")

            # 8. Clear cart and start over with a new product selection

            data['Select'].clear()
            data['Add Cart'].clear()
            data['Remove'].clear()
            data['Order'].clear()
        else:
            raise ValueError("Task not found")

        interactions.append(10)
        # create interaction
        if n == 1:
            return data 
        else:
            n-=1
            idx = tasks.index(task)
            prob = transition[:,idx].copy()
            next_task = np.random.choice(tasks, p=prob, replace=False)
            return trajectory(next_task, n, data, interactions)
        
    ww = trajectory(random.choice(tasks), n_interactions, 
               {'Select': [], 'Save': [], 'Add Cart': [], 'Remove': [], 'Order': []}, interactions=[])
    
    # Select
    # Save
    # Add card
    
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