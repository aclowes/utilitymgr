import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from utilitymgr import utils

download_script = """
svc = new DataDownloadService(app.logger);
reqObj = {
fileFormat: "XML Format (.xml)",
serviceAccountAddress: {},
serviceAccountNumber: "%s",
startDate: "%s",
endDate: "%s"
};
return await svc.getDataDownloadFile(reqObj);    
"""


def main():
    driver = webdriver.Chrome('./chromedriver')
    driver.implicitly_wait(10)  # seconds
    driver.get('https://www.sce.com/')
    username = driver.find_element(By.NAME, 'username')
    username.send_keys(os.environ['SCE_USERNAME'])
    password = driver.find_element(By.NAME, 'password')
    password.send_keys(os.environ['SCE_PASSWORD'])
    password.send_keys('\n')
    driver.find_element(By.ID, 'accountDetailsPopupLink')
    driver.get('https://www.sce.com/sma/ESCAA/EscGreenButtonData')
    time.sleep(2)
    for account in os.environ['SCE_ACCOUNTS'].split(' '):
        start_date, end_date = map(lambda x: x.strftime('%m/%d/%y'), utils.week_start_end())
        script = download_script % (account, start_date, end_date)
        response = driver.execute_script(script)
        with open(f'data/sce_{account}.xml', 'w') as data_file:
            data_file.write(response)


def rtp():
    html = open('index.html').read()
    page = requests.get('https://www.sce.openadr.com/dr.website/scepr-event-status.jsf#')
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="tempDatetime").find(class_="tempDatetimeBottom")
    days = [results.text.split(" ")[0].lower().strip()]
    results = soup.find(id="RTPForecastDIV").find_all(class_="rich-table-row")
    for day in results[:4]:
        days.append(day.find_all("td")[1].text.split(" ")[0].lower())
    text = ", ".join(days)
    html = html.replace('Pricing', f"Pricing next five days: {text}")
    open('data/index.html', 'w').write(html)


if __name__ == '__main__':
    main()
    # rtp()
