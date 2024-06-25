import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.3"}

def fetch_price(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        # Extract the price whole part
        price_whole = soup.find(class_="a-price-whole").get_text().strip()
        price_whole = ''.join(filter(str.isdigit, price_whole))

        # Extract the price decimal part if available
        price_decimal = soup.find(class_="a-price-decimal")
        if price_decimal:
            price_decimal = price_decimal.get_text().strip()
            price_decimal = ''.join(filter(str.isdigit, price_decimal))
        else:
            price_decimal = '00'

        # Combine the whole and decimal parts
        price = price_whole + "." + price_decimal

        return float(price)  # Convert to float
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def fetch_object_name(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        # Extract the first 20 chars of the title
        object_name = soup.find(id="productTitle").get_text().strip()
        object_name = object_name[:20]

        return object_name
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def fetch_asin(url):
    try:
        response = requests.get(url, headers=headers, allow_redirects=True)

        # Get the final URL after redirects
        final_url = response.url
        print(f"Final URL after redirects: {final_url}")

        asin_match = re.search(r'/dp/([A-Z0-9]{10})', final_url)

        if asin_match:
            asin = asin_match.group(1)
            print(f'Extracted ASIN: {asin}')
            return asin
        else:
            print('ASIN not found in the URL.')
            return None

    except Exception as e:
        print(f"Error fetching ASIN: {e}")
        return None
