import requests
from bs4 import BeautifulSoup

# Send a GET request to the URL
url = "https://www.centar-tehnike.hr/proizvodi/televizori-smart-tv/"
#request_headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Find all the television items
tv_items = soup.find_all("h2", class_="cp-title")

tv_items1 = soup.find_all("div", class_="clear cp-cnt")

# Extract data from each television item
for tv in tv_items:
    print(tv.text)

# Extract data from each television item
for tv in tv_items1:
    name = tv.text
    #price = tv.find("span", class_="price").text.strip()
    #specifications = tv.find("div", class_="description").text.strip()

    print("Name:", name)
    print("Price:", price)
    print("Specifications:", specifications)
    print()

print(tv_items)