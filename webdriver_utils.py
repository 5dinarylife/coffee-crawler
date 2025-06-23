import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_chromedriver():
    """
    Sets up and returns a Selenium Chrome webdriver optimized for Streamlit Cloud.
    This version explicitly sets a unique --user-data-dir to resolve the
    persistent SessionNotCreatedException.
    """
    chrome_options = Options()
    
    # --- General headless options ---
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--remote-debugging-port=9222")

    # --- Critical fix for the "user data directory" error ---
    # By specifying a unique, temporary directory for each run, we avoid conflicts.
    user_data_dir = f"/tmp/selenium_user_data_{random.randint(10000, 99999)}"
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # --- Other stability options ---
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver 