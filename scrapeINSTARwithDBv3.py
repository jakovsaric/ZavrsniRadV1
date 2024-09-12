import requests
from bs4 import BeautifulSoup
import sqlite3
import re

# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS productsInstar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 price FLOAT NOT NULL,
                 screen_size INTEGER NOT NULL DEFAULT 0,
                 manufacturer TEXT NOT NULL DEFAULT 'Other',
                 screen_type TEXT NOT NULL DEFAULT 'Other',
                 tv_code TEXT NOT NULL DEFAULT 'Unknown',
                 product_link TEXT NOT NULL DEFAULT 'Unknown',
                 image_link TEXT NOT NULL DEFAULT 'Unknown',
                 store TEXT NOT NULL DEFAULT 'Instar')''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link):
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO productsInstar (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link, store) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link, 'Instar'))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Product '{name}' already exists in the database. Skipping.")
    conn.close()

# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("DELETE FROM productsInstar")
    conn.commit()
    conn.close()

# Function to fetch a page and return the BeautifulSoup object
def fetch_page(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

# Function to extract products from a given BeautifulSoup object
def extract_products(soup):
    products = []
    product_items = soup.find_all("div", class_="product-item-box")
    print(f"Found {len(product_items)} products on the page.")  # Debug information
    for item in product_items:
        try:
            name_tag = item.find("h2", class_="title")
            name_span = name_tag.find("span")
            name = name_span.text.strip()

            # Extract product link
            product_link_tag = name_tag.find("a", class_="productEntityClick")
            product_link = "https://www.instar-informatika.hr" + product_link_tag["href"] if product_link_tag else "Unknown"

            # Extract image link
            image_tag = item.find("img", class_="img-fluid productEntityClick")
            image_link = image_tag["src"] if image_tag else "Unknown"

            # Extract price
            price_span = item.find("span", class_="standard-price price-akcija order-2")
            if not price_span:
                price_span = item.find("span", class_="standard-price priceregular order-2")
            price_str = price_span.text.strip() if price_span else "0,00 €"
            price_float = parse_price(price_str)

            # Extract screen size
            screen_size_tag = item.find("li", string=re.compile(r"Dijagonala:"))
            screen_size = extract_screen_size(screen_size_tag.text) if screen_size_tag else 0

            # Extract manufacturer
            manufacturer = extract_manufacturer(name) or "Other"

            # Extract screen type
            screen_type_tag = item.find("li", string=re.compile(r"Panel:"))
            screen_type = extract_screen_type(screen_type_tag.text) if screen_type_tag else "Other"

            # Extract TV code
            tv_code = extract_tv_code(name, manufacturer, screen_size)

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
    return re.sub(r'(?<=\?page=)\d+', str(next_page), current_url)

# Function to check if a product already exists in the database
def product_exists(name):
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM productsInstar WHERE name = ?", (name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Helper functions to extract additional information
def extract_screen_size(text):
    match = re.search(r'(\d{2,3})"', text)
    return int(match.group(1)) if match else 0

def extract_manufacturer(name):
    manufacturers = ["Samsung", "LG", "Tesla", "Sony", "Philips", "Hisense", "TCL", "Vivax", "Panasonic"]
    for manufacturer in manufacturers:
        if manufacturer in name:
            return manufacturer
    return "Other"

def extract_screen_type(text):
    match = re.search(r"Panel: (\w+)", text)
    return match.group(1) if match else "Other"


def extract_tv_code(name, manufacturer, screen_size):
    # Remove "TV", the manufacturer, and screen size from the name
    name = re.sub(r'TV|,.*|' + manufacturer + r'|\b' + str(screen_size) + r'"', '', name).strip()

    # Split the name by spaces
    parts = name.split()

    # Filter out any parts that consist only of letters
    filtered_parts = [part for part in parts if not part.isalpha()]

    # Join the filtered parts back into a single string
    return ' '.join(filtered_parts)


# URL of the initial webpage to scrape
base_url = "https://www.instar-informatika.hr/svi-televizori/260/?p=12&s=24"

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

    # Print the current URL for debugging purposes
    print(f"Fetching URL: {current_url}")

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
    next_page_link = soup.find("a", class_="next")
    if next_page_link:
        current_url = next_page_link["href"]
        current_page += 1
    else:
        current_url = None

print("Data has been successfully stored in the database.")
