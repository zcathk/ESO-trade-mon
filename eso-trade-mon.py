import requests
from bs4 import BeautifulSoup
import time
import smtplib
import logging
import random
import time
import yaml

with open('eso-trade-items.yaml') as f:    
    data = yaml.load(f, Loader=yaml.FullLoader)
logFile = 'eso-trade-mon.log'
logging.basicConfig( filename = logFile,filemode = 'w',level = logging.INFO,format = '%(asctime)s - %(levelname)s: %(message)s',\
                     datefmt = '%d/%I:%M:%S%p' )
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; MI 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36'}
logging.info('================= LOG STARTING ==============')
count = 0 
while (count < len(data['esosearches'])):
    itemName = data['esosearches'][count]['itemName']
    priceThershold = data['esosearches'][count]['priceThershold']
    minThershold = data['esosearches'][count]['minThershold']
    url = data['esosearches'][count]['url']
    #logging.info('URL :' + url)
    
    waitsec = random.randint(1,30)
    logging.info('wait for :' + str(waitsec))
    time.sleep(int(waitsec))
    
    logging.info('Fetching item: ' + itemName)
    response = requests.get(url, headers=headers)    
    soup = BeautifulSoup(response.text, "lxml")        
    str_soup = str(soup)    
    with open("verify_response.html", "w") as file:
        file.write(str_soup)    
    if str(soup).find("recaptcha") > -1:      
        logging.info('!!! Blocked by re-captcha !!! ')    
        exit()

    subject = ""
    subjloc = ""
    content = ""
    rec_found= 0
    table = soup.find('table', attrs={'class':'trade-list-table max-width'})
    if table:
        table_rows = table.find_all('tr')     
        for tr in table_rows:        
            td = tr.find_all('td')
            row = [i for i in td]
            if len(row) == 5:        
                minutes=int(row[4].attrs.get('data-mins-elapsed'))
                rec_found = rec_found + 1
                logging.info("Found Item last seen " + str(minutes) + " Mins" + ';loc:' + " ".join(row[2].text.split()) + ";Cost " + " ".join(row[3].text.split()))
                if minutes < minThershold:
                    if not subject:
                        subjloc= row[2].text
                        subject= itemName + ';' + str(minutes) + '; ' + ';' + " ".join(row[2].text.split()) + ";" + " ".join(row[3].text.split())
                    else:
                        content=content+'Min:' + str(minutes) + '; ' + 'loc:' + " ".join(row[2].text.split()) +'\n' + 'Cost:' + " ".join(row[3].text.split()) +'\n'
    logging.info(str(rec_found) + ' rec less then ' + str(priceThershold) + 'g.')
    if subject and subjloc:
        fromaddr = 'zcat_demo@hotmail.com'
        toaddrs  = 'zcat_demo@yahoo.com'
        msg = 'Subject:' + subject + """\n
    """ + content
        logging.info("Sending email with msg:" + msg)
        server = smtplib.SMTP('smtp.live.com', 587)
        server.starttls()
        server.login("zcat_demo@hotmail.com", "demo_password")        
        server.sendmail('zcat_demo@hotmail.com', toaddrs, msg)
        server.quit()    
        logging.info("email sent.")
    else:
        logging.info('No item fit criteria (elapse<' + str(minThershold) + ' minutes). No email sent.')
    count = count + 1
    logging.info("count:" + str(count))

logging.info("--exiting--")
exit()
