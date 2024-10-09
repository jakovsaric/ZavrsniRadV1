import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = "https://www.centar-tehnike.hr/proizvodi/televizori-smart-tv/"

# Set headers to mimic a legitimate browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99"
                  " Safari/537.36"
}

# Send a GET request to the URL
response = requests.get(url, headers=headers)

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Find all product articles
product_articles = soup.find_all("article", class_="cp")

# Extract data from each product article
for article in product_articles:
    # Extract product details
    name = article.find("h2", class_="cp-title").text.strip()
    price = article.find("div", class_="modal-price-main").text.strip().split("\n")[-1].strip()
    # specs = [spec.text.strip() for spec in article.find("ul", class_="cp-attrs").find_all("li")]

    # Print product details
    print("Name:", name)
    print("Price:", price)
    # print("Specifications:", specs)
    print()
