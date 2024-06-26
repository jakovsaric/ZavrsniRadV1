import requests
from bs4 import BeautifulSoup
import sqlite3
import re

# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsDBv2.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 price FLOAT)''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(name, price):
    conn = sqlite3.connect("productsDBv2.db")
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsDBv2.db")
    c = conn.cursor()
    c.execute("DELETE FROM products")
    conn.commit()
    conn.close()

# URL of the webpage to scrape
base_url = "https://www.centar-tehnike.hr/proizvodi/televizori-smart-tv/"
load_more_url_template = "https://www.centar-tehnike.hr/proizvodi/televizori-smart-tv/?page={}"

# Set headers to mimic a legitimate browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
}

# Function to fetch a page and return the BeautifulSoup object
def fetch_page(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

# Function to extract products from a given BeautifulSoup object
def extract_products(soup):
    products = []
    product_articles = soup.find_all("article", class_="cp")
    for article in product_articles:
        name = article.find("h2", class_="cp-title").text.strip()
        price_str = article.find("div", class_="modal-price-main").text.strip().split("\n")[-1].strip()
        price_float = float(re.sub(r"[^\d,]", "", price_str).replace(",", "."))  # Adjust the price extraction
        products.append((name, price_float))
    return products

# Function to get the next page URL from the soup
def get_next_page_url(soup, current_page, total_pages):
    if current_page < total_pages:
        return load_more_url_template.format(current_page + 1)
    return None

# Clear existing data from the database
clear_data()

# Create table in the database
create_table()

# Initialize URL and soup object
current_url = base_url
soup = fetch_page(current_url)

# Extract the total number of pages from the initial load
total_pages = int(soup.find("div", {"data-infinitescroll_total_pages": True}).get("data-infinitescroll_total_pages", "1"))
current_page = 1

# Keep fetching and extracting products until no more pages
while current_url:
    products = extract_products(soup)
    for name, price in products:
        insert_data(name, price)
        print("Name:", name)
        print("Price:", "{:.2f}".format(price))
        print()

    # Get the next page URL
    current_page += 1
    current_url = get_next_page_url(soup, current_page, total_pages)
    if current_url:
        soup = fetch_page(current_url)

print("Data has been successfully stored in the database.")
