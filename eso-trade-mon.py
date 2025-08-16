import logging
import random
import smtplib
import time
import yaml
import requests
from bs4 import BeautifulSoup


# ==============================
# Load Configuration
# ==============================
CONFIG_FILE = "eso-trade-items.yaml"
LOG_FILE = "eso-trade-mon.log"

with open(CONFIG_FILE, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# ==============================
# Logging Setup
# ==============================
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%d/%I:%M:%S%p"
)
logging.info("===== LOG STARTING =====")

# ==============================
# HTTP Headers
# ==============================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; MI 9) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/87.0.4280.101 Mobile Safari/537.36"
    )
}

# ==============================
# Main Script
# ==============================
for idx, search_item in enumerate(config.get("esosearches", []), start=1):
    item_name = search_item["itemName"]
    price_threshold = search_item["priceThershold"]
    min_threshold = search_item["minThershold"]
    url = search_item["url"]

    wait_sec = random.randint(1, 30)
    logging.info(f"Waiting for {wait_sec} seconds before fetching...")
    time.sleep(wait_sec)

    logging.info(f"Fetching item: {item_name}")
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "lxml")

    # Save for verification/debug
    with open("verify_response.html", "w") as file:
        file.write(str(soup))

    # Check for captcha
    if "recaptcha" in str(soup).lower():
        logging.error("Blocked by reCAPTCHA! Exiting.")
        exit()

    subject = ""
    subj_loc = ""
    content = ""
    records_found = 0

    table = soup.find("table", attrs={"class": "trade-list-table max-width"})
    if table:
        for tr in table.find_all("tr"):
            td_elements = tr.find_all("td")
            if len(td_elements) == 5:
                minutes = int(td_elements[4].attrs.get("data-mins-elapsed"))
                location = " ".join(td_elements[2].text.split())
                cost = " ".join(td_elements[3].text.split())

                records_found += 1
                logging.info(f"Found Item last seen {minutes} mins; loc: {location}; Cost: {cost}")

                if minutes < min_threshold:
                    if not subject:
                        subj_loc = location
                        subject = f"{item_name};{minutes};;{location};{cost}"
                    else:
                        content += f"Min: {minutes}; loc: {location}\nCost: {cost}\n"

    logging.info(f"{records_found} records under {price_threshold}g.")

    if subject and subj_loc:
        from_addr = "zcat_demo@hotmail.com"
        to_addr = "zcat_demo@yahoo.com"
        msg = f"Subject: {subject}\n\n{content}"

        try:
            logging.info(f"Sending email to {to_addr} with message:\n{msg}")
            with smtplib.SMTP("smtp.live.com", 587) as server:
                server.starttls()
                server.login(from_addr, "demo_password")
                server.sendmail(from_addr, to_addr, msg)
            logging.info("Email sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
    else:
        logging.info(f"No item met criteria (elapsed < {min_threshold} mins). No email sent.")

    logging.info(f"Processed search {idx} of {len(config['esosearches'])}")

logging.info("-- Exiting Script --")
exit()
