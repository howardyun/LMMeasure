import requests
from bs4 import BeautifulSoup

# URL of the website
url = "https://civitai.com/"

# Send a request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    print(soup)
    # Find all model cards on the main page
    model_cards = soup.find_all("div", class_="model-card")

    # Check if model cards are found
    if model_cards:
        for model in model_cards:
            # Extract title and link
            title = model.find("h2").text if model.find("h2") else "No title"
            link = model.find("a", href=True)["href"] if model.find("a", href=True) else "No link"
            print(f"Title: {title}, Link: {url}{link}")
    else:
        print("No model cards found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
