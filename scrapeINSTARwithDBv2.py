import requests
from bs4 import BeautifulSoup
import sqlite3


# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsINSTARDBv2.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE,
                 price FLOAT)''')
    conn.commit()
    conn.close()


# Function to insert data into the database
def insert_data(name, price):
    conn = sqlite3.connect("productsINSTARDBv2.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Product '{name}' already exists in the database. Skipping.")
    conn.close()


# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsINSTARDBv2.db")
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
    product_items = soup.find_all("div", attrs={"data-product_name": True})
    for item in product_items:
        name = item["data-product_name"]
        price_str = item.find("span", class_="standard-price").text.strip()

        # Remove thousand separators and convert price to float
        price_str = price_str.replace(".", "").replace(",", ".").replace(" €", "")
        price_float = float(price_str)

        products.append((name, price_float))
    return products


# Function to get the next page URL
def get_next_page_url(current_page, page_size, total_no):
    next_page = current_page + 1
    calc_page = (total_no + page_size - 1) // page_size  # Calculate total pages
    if next_page <= calc_page:
        query_params = f"?p={next_page}&s={page_size}"
        return base_url + query_params
    return None


# Function to check if a product already exists in the database
def product_exists(name):
    conn = sqlite3.connect("productsINSTARDBv2.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM products WHERE name = ?", (name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


# URL of the initial webpage to scrape
base_url = "https://www.instar-informatika.hr/svi-televizori/260/"

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
soup = fetch_page(current_url)

# Extract initial page details
page_size = 24  # As defined in the JavaScript
total_no = 198  # As defined in the JavaScript
current_page = 1

# Extract products from the first page
products = extract_products(soup)
for name, price in products:
    if not product_exists(name):
        insert_data(name, price)
        print("Name:", name)
        print("Price:", "{:.2f}".format(price))
        print()
    else:
        print(f"Product '{name}' already exists in the database. Skipping.")

# Fetch and extract products from subsequent pages
while current_page * page_size < total_no:
    current_url = get_next_page_url(current_page, page_size, total_no)
    if current_url:
        soup = fetch_page(current_url)
        products = extract_products(soup)
        for name, price in products:
            if not product_exists(name):
                insert_data(name, price)
                print("Name:", name)
                print("Price:", "{:.2f}".format(price))
                print()
            else:
                print(f"Product '{name}' already exists in the database. Skipping.")
        current_page += 1

print("Data has been successfully stored in the database.")
