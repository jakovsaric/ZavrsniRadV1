import requests
from bs4 import BeautifulSoup
import sqlite3
import re

# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS productsSanctaDomenica
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 price FLOAT NOT NULL,
                 screen_size INTEGER NOT NULL DEFAULT 0,
                 manufacturer TEXT NOT NULL DEFAULT 'Other',
                 screen_type TEXT NOT NULL DEFAULT 'Other',
                 tv_code TEXT NOT NULL DEFAULT 'Unknown',
                 product_link TEXT NOT NULL DEFAULT 'Unknown',
                 image_link TEXT NOT NULL DEFAULT 'Unknown')''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link):
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO productsSanctaDomenica (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Product '{name}' already exists in the database. Skipping.")
    conn.close()

# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("DELETE FROM productsSanctaDomenica")
    conn.commit()
    conn.close()

# Function to fetch a page and return the BeautifulSoup object
def fetch_page(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

# Function to extract products from a given BeautifulSoup object
def extract_products(soup):
    products = []
    product_items = soup.find_all("li", class_="item product product-item")
    for item in product_items:
        try:
            name_tag = item.find("strong", class_="product name product-item-name")
            name = name_tag.text.strip()

            # Extract product link
            product_link_tag = name_tag.find("a", class_="product-item-link")
            product_link = product_link_tag["href"] if product_link_tag else "Unknown"

            # Extract image link
            image_tag = item.find("img", class_="photo image")
            image_link = image_tag["src"] if image_tag else "Unknown"

            # Extract price
            special_price_span = item.find("span", class_="special-price")
            if special_price_span:
                price_str = special_price_span.find("span", class_="price").text.strip()
                price_float = parse_price(price_str)
            else:
                # Extract price from alternative structure if special-price span not found
                price_div = item.find("div", class_="price-box price-final_price")
                if price_div:
                    price_span = price_div.find("span", class_="price")
                    if price_span:
                        price_str = price_span.text.strip()
                        price_float = parse_price(price_str)
                    else:
                        price_float = 0.0  # Default to 0.0 if price span is not found
                else:
                    price_float = 0.0  # Default to 0.0 if price structure is not found

            # Extract screen size
            screen_size = extract_screen_size(name) or 0

            # Extract manufacturer
            manufacturer = extract_manufacturer(name) or "Other"

            # Extract screen type
            screen_type = extract_screen_type(name) or "Other"

            # Extract TV code
            tv_code = extract_tv_code(name, manufacturer) or "Unknown"

            products.append((name, price_float, screen_size, manufacturer, screen_type, tv_code, product_link, image_link))
        except Exception as e:
            print(f"Error processing item: {e}")
    return products

# Function to parse the price string into a float
def parse_price(price_str):
    # Match price with or without thousands separator and with a decimal comma
    match = re.search(r'\d{1,3}(?:\.\d{3})*(?:,\d+)?', price_str)
    if match:
        cleaned_price = match.group().replace(".", "").replace(",", ".")
        return float(cleaned_price)
    else:
        raise ValueError(f"Could not parse price string: {price_str}")

# Function to get the next page URL
def get_next_page_url(current_url, current_page):
    next_page = current_page + 1
    return re.sub(r'(?<=\?p=)\d+', str(next_page), current_url)

# Function to check if a product already exists in the database
def product_exists(name):
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM productsSanctaDomenica WHERE name = ?", (name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Helper functions to extract additional information
def extract_screen_size(name):
    match = re.search(r'(\d{2,3})"', name)
    if not match:
        match = re.search(r"(\d{2,3})''", name)
    return int(match.group(1)) if match else -1

def extract_manufacturer(name):
    manufacturers = ["Samsung", "LG", "Tesla", "Sony", "Philips", "Hisense", "TCL", "VIVAX", "Panasonic"]
    for manufacturer in manufacturers:
        if manufacturer in name:
            return manufacturer
    return "Other"

def extract_screen_type(name):
    screen_types = ["FULL HD", "NANOCELL", "QNED", "ULED", "OLED", "QLED", "MINI LED", "MINILED", "LED"]
    for screen_type in screen_types:
        if screen_type in name.upper():
            return screen_type
    return "Other"

def extract_tv_code(name, manufacturer):
    code_match = re.search(rf'{manufacturer} (.*)', name)
    if code_match:
        return manufacturer + ' ' + code_match.group(1).strip()
    return "Unknown"

# URL of the initial webpage to scrape
base_url = "https://www.sancta-domenica.hr/televizori/led-tv.html"

# Set headers to mimic a legitimate browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
}

# Clear existing data from the database
clear_data()

# Create table in the database
create_table()

# Initialize URL and fetch the first page
current_url = base_url
current_page = 1

while current_url:
    # Fetch the current page
    soup = fetch_page(current_url)

    # Extract products from the current page
    products = extract_products(soup)

    # Process each product
    for name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link in products:
        if not product_exists(name):
            insert_data(name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link)
            print("Name:", name)
            print("Price:", "{:.2f}".format(price))
            print("Screen Size:", screen_size)
            print("Manufacturer:", manufacturer)
            print("Screen Type:", screen_type)
            print("TV Code:", tv_code)
            print("Product Link:", product_link)
            print("Image Link:", image_link)
            print()
        else:
            print(f"Product '{name}' already exists in the database. Skipping.")

    # Find the URL of the next page
    next_page_link = soup.find("a", class_="action next")
    if next_page_link:
        current_url = next_page_link["href"]
        current_page += 1
    else:
        current_url = None

print("Data has been successfully stored in the database.")
