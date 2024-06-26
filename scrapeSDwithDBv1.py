import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import sys


# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsSanctaDomenicaDBv1.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE,
                 price FLOAT)''')
    conn.commit()
    conn.close()


# Function to insert data into the database
def insert_data(name, price):
    conn = sqlite3.connect("productsSanctaDomenicaDBv1.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Product '{name}' already exists in the database. Skipping.")
    conn.close()


# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsSanctaDomenicaDBv1.db")
    c = conn.cursor()
    c.execute("DELETE FROM products")
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
            name = item.find("strong", class_="product name product-item-name").text.strip()

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
                        price_float = None  # Handle case where price span is not found
                else:
                    price_float = None  # Handle case where price structure is not found

            products.append((name, price_float))
        except:
            print("Nešto ne valja")
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
    conn = sqlite3.connect("productsSanctaDomenicaDBv1.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM products WHERE name = ?", (name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


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
    for name, price in products:
        if not product_exists(name):
            insert_data(name, price)
            print("Name:", name)
            print("Price:", "{:.2f}".format(price))
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
