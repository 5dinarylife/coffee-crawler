from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

def get_chromedriver():
    """
    Final attempt to create a stable webdriver for Streamlit Cloud.
    Uses a minimal set of proven options and the ChromeService object for robust control.
    """
    options = Options()
    
    # Minimal set of options proven to work in sandboxed environments like Docker/Streamlit Cloud
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Using the Service object for more robust initialization
    service = ChromeService()
    
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver 