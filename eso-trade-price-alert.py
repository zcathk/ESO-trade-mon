import logging
import random
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time,os
import eso_trade_utils

# Main . Start with constants and var initialziation
# ==============================
CONFIG_FILE = "eso-trade-items.yml"
LOG_FILE = "eso-trade-mon.log"
emailbody=""

# Logging Setup
# ==============================
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%m/%d/%y-%I:%M:%S%p"
)
logging.info("===== LOG STARTING =====")
# Initialize env var
# ==============================
from_gmail=os.getenv("FROM_GMAILADDR")
from_credential=os.getenv("FROM_CREDENTIAL")
to_email=os.getenv("TO_EMAILADDR")
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Example: run Chrome in headless mode
chrome_options.add_argument("--window-size=1280,960")
service = Service(executable_path=os.getenv("PATH_TO_WEBDRIVER"))
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chrome_options)
with open(CONFIG_FILE, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
# Process each item listed from input file
# ==============================
for idx, search_item in enumerate(config.get("esosearches", []), start=1):
    item_name = search_item["itemName"]
    min_threshold = search_item["minThershold"]
    url = search_item["url"]
    
    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
    # Wait until browser fully rendered
    time.sleep(5)
    # capture page source for audit
    with open("eso-trade-price-alert_source.html", "w") as file:
        file.write(driver.page_source)   
    try: 
        table = driver.find_element(By.XPATH, '//*[@id="search-result-view"]/div[1]/div/div/table')
        if table:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows[1:4]:   # skip header row and first few rec only
                cols = row.find_elements(By.TAG_NAME, "td")    
                if len(cols)>=5 :
                    item=cols[0].text.replace("\n", " ")
                    location=cols[2].text.replace("\n", " ")
                    priceunits=cols[3].text.replace("\n", " ")
                    seenmin=eso_trade_utils.time_ago_to_minutes(cols[4].text)
                    if seenmin < min_threshold :
                        emailbody += f"Item: {item}| Min: {seenmin}| loc: {location}| Cost: {priceunits}\n"
    except Exception as e:
        logging.error(f"Result table not found: {e}")  
    wait_sec = random.randint(1, 4)
    logging.info(f"Waiting for {wait_sec} seconds before fetching...")
    time.sleep(wait_sec)

# Send email notif when anything worth found.
if emailbody !="":
    try:
        logging.info(f"Sending email with body"+emailbody)
        eso_trade_utils.sendnoti("My ESO Trade price drop alert",emailbody, from_gmail,from_credential,to_email)
        logging.info(f"Email sent.")
    except Exception as e:
        logging.error(f"Sending email exception: {e}")  

# Close the browser
driver.quit()

