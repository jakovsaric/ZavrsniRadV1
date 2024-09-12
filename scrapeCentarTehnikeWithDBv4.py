import requests
from bs4 import BeautifulSoup
import sqlite3
import re

# Function to create a database table
def create_table():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS productsCentarTehnike
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 price FLOAT NOT NULL,
                 screen_size INTEGER NOT NULL DEFAULT 0,
                 manufacturer TEXT NOT NULL DEFAULT 'Other',
                 screen_type TEXT NOT NULL DEFAULT 'Other',
                 tv_code TEXT NOT NULL DEFAULT 'Unknown',
                 product_link TEXT NOT NULL DEFAULT 'Unknown',
                 image_link TEXT NOT NULL DEFAULT 'Unknown',
                 store TEXT NOT NULL DEFAULT 'Centar Tehnike')''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link):
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO productsCentarTehnike (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link, store) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link, 'Centar Tehnike'))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Product '{name}' already exists in the database. Skipping.")
    conn.close()

# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("DELETE FROM productsCentarTehnike")
    conn.commit()
    conn.close()

# Function to fetch a page and return the BeautifulSoup object
def fetch_page(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

# Function to extract screen size from the HTML string
def extract_screen_size(html_string):
    pattern = r'\d+\s*"'
    match = re.search(pattern, html_string)
    if match:
        size_str = match.group(0).strip().replace('"', '').strip()
        return int(size_str)
    return None

# Function to extract products from a given BeautifulSoup object
def extract_products(soup):
    products = []
    product_articles = soup.find_all("article", class_="cp")
    for article in product_articles:
        try:
            name = article.find("h2", class_="cp-title").text.strip()

            # Extract product link
            product_link_tag = article.find("a", class_="cp-header-cnt")
            product_link = product_link_tag["href"] if product_link_tag else "Unknown"

            # Extract image link
            image_tag = article.find("div", class_="cp-image").find("img")
            image_link = image_tag["src"] if image_tag else "Unknown"

            # Extract price
            price_str = article.find("div", class_="modal-price-main").text.strip().split("\n")[-1].strip()
            price_float = float(re.sub(r"[^\d,]", "", price_str).replace(",", "."))

            # Extract screen size
            screen_size_tag = None
            for li in article.find_all("li", class_="cp-attr"):
                if "cm" in li.text or '"' in li.text:  # Check for keywords indicating screen size
                    screen_size_tag = li
                    break
            screen_size = extract_screen_size(screen_size_tag.text) if screen_size_tag else 0

            # Extract manufacturer
            manufacturer_tag = article.find("span", {"data-product_manufacturer_title": True})
            manufacturer = manufacturer_tag.text.strip() if manufacturer_tag else "Other"

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
    match = re.search(r'\d{1,3}(?:\.\d{3})*(?:,\d+)?', price_str)
    if match:
        cleaned_price = match.group().replace(".", "").replace(",", ".")
        return float(cleaned_price)
    else:
        raise ValueError(f"Could not parse price string: {price_str}")

# Function to get the next page URL from the soup
def get_next_page_url(soup, current_page, total_pages):
    if current_page < total_pages:
        return load_more_url_template.format(current_page + 1)
    return None

# Function to check if a product already exists in the database
def product_exists(name):
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM productsCentarTehnike WHERE name = ?", (name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Helper functions to extract additional information
def extract_screen_type(name):
    screen_types = ["FULL HD", "NANOCELL", "QNED", "ULED", "OLED", "QLED", "MINI LED", "MINILED", "LED"]
    for screen_type in screen_types:
        if screen_type in name.upper():
            return screen_type
    return "Other"


def extract_tv_code(name, manufacturer):
    # Remove "(izlog)" from the name if it exists
    name = name.replace("(izlog)", "").strip()

    # Find the part of the string after the manufacturer's name
    code_match = re.search(rf'{manufacturer}\s+(.*)', name)
    if code_match:
        # Split the string into parts using space as a delimiter
        parts = code_match.group(1).strip().split()

        # Filter the parts based on the given conditions
        filtered_parts = [
            part for part in parts
            if len(part) > 4 and not part.isalpha()  # Length > 4 and not just letters
        ]

        # Join the filtered parts back into a string
        if filtered_parts:
            return ' '.join(filtered_parts)  # Manufacturer is removed here

    return "Unknown"

# URL of the initial webpage to scrape
base_url = "https://www.centar-tehnike.hr/proizvodi/televizori-smart-tv/"
load_more_url_template = "https://www.centar-tehnike.hr/proizvodi/televizori-smart-tv/?page={}"

# Set headers to mimic a legitimate browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
}

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

    # Get the next page URL
    current_page += 1
    current_url = get_next_page_url(soup, current_page, total_pages)
    if current_url:
        soup = fetch_page(current_url)

print("Data has been successfully stored in the database.")
