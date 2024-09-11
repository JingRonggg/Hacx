import requests
import socket
from urllib.parse import urlparse

# IP2Location API Key
IP2LOCATION_API_KEY = "0A5A3D6B8FB21932446B10ECEC011B22"
IP2LOCATION_BASE_URL = "https://api.ip2location.io/"

# Azure Maps API Key
AZURE_MAPS_API_KEY = "6GsdEyPLAaRmAyUpLIFCQWO2bbs1NpByhwcIm6tIZHy3bQIibUDeJQQJ99AIACrJL3JR32hfAAAgAZMPEgbQ"  # Replace with your Azure Maps key
AZURE_MAPS_BASE_URL = "https://atlas.microsoft.com/search/address/reverse/json"

# Function to resolve domain to IP address
def get_ip_from_url(url):
    try:
        # Extract domain from the URL
        domain = urlparse(url).netloc
        # Resolve the domain to an IP address
        ip_address = socket.gethostbyname(domain)
        print(f"Resolved IP Address: {ip_address}")
        return ip_address
    except socket.gaierror as err:
        print(f"Error resolving IP address for {url}: {err}")
        return None

# Function to get geolocation, ISP, and ASN from IP address using IP2Location
def get_ip_geolocation(ip_address):
    url = f"{IP2LOCATION_BASE_URL}?key={IP2LOCATION_API_KEY}&ip={ip_address}&format=json"
    
    try:
        # Send a GET request to the IP2Location API
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract latitude, longitude, ISP, and ASN
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        isp = data.get('isp')
        asn = data.get('asn')

        # Print out the geolocation, ISP, and ASN data
        print(f"Latitude, Longitude: {latitude}, {longitude}")
        print(f"ISP: {isp}")
        print(f"ASN: {asn}")
        
        return latitude, longitude, isp, asn

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# Function to get the address from latitude and longitude using Azure Maps
def get_address_from_coordinates(latitude, longitude):
    url = f"{AZURE_MAPS_BASE_URL}?api-version=1.0&query={latitude},{longitude}&subscription-key={AZURE_MAPS_API_KEY}"
    
    try:
        # Send a GET request to the Azure Maps Reverse Geocoding API
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract the formatted address
        if data.get('addresses'):
            address = data['addresses'][0]['address']['freeformAddress']
            print(f"Address: {address}")
        else:
            print("No address found for the given coordinates.")
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# Main function to handle input and call geolocation and reverse geocoding
def main():
    # url = input("Enter the URL: ")
    ip = input("Enter the ip: ")
    # Resolve the domain to an IP address
    # ip_address = get_ip_from_url(url)
    latitude, longitude, isp, asn = get_ip_geolocation(ip)

    # if ip_address:
    #     # Get latitude, longitude, ISP, and ASN from IP address
    #     latitude, longitude, isp, asn = get_ip_geolocation(ip_address)
        
    #     if latitude and longitude:
    #         # Get the address from latitude and longitude using Azure Maps
    #         get_address_from_coordinates(latitude, longitude)

if __name__ == "__main__":
    main()
