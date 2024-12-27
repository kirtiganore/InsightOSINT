from bs4 import BeautifulSoup
import requests

def crawl_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = [tag.text for tag in soup.find_all('h1')]
        return {"status": "success", "titles": titles}
    except Exception as e:
        return {"status": "error", "message": str(e)}
