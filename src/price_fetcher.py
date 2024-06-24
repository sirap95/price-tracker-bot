import requests
from bs4 import BeautifulSoup
def fetch_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"}
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        # Extract the first 20 chars of the title
        object_name = soup.find(id="productTitle").get_text().strip()
        object_name =  object_name[:20]

        return object_name
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None
