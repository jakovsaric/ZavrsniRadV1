import requests
from bs4 import BeautifulSoup
import sqlite3

# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsINSTARDBv2.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 price FLOAT)''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(name, price):
    conn = sqlite3.connect("productsINSTARDBv2.db")
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsINSTARDBv2.db")
    c = conn.cursor()
    c.execute("DELETE FROM products")
    conn.commit()
    conn.close()

# URL of the webpage to scrape
url = "https://www.instar-informatika.hr/svi-televizori/260/"

# Set headers to mimic a legitimate browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
}

# Send a GET request to the URL
response = requests.get(url, headers=headers)

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Find all product items
product_items = soup.find_all("div", attrs={"data-product_name": True})

# Clear existing data from the database
#clear_data()

# Create table in the database
create_table()

# Extract data from each product item and store in the database
for item in product_items:
    # Extract product details
    name = item["data-product_name"]
    price_str = item.find("span", class_="standard-price").text.strip()

    # Convert price string to float
    price_float = float(price_str.replace(",", ".").replace(" €", ""))

    # Insert data into the database
    insert_data(name, price_float)

    # Print product details
    print("Name:", name)
    print("Price:", "{:.2f}".format(price_float))
    print()

print("Data has been successfully stored in the database.")
