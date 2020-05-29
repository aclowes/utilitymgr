import os
import time
import datetime

from selenium import webdriver

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
    username = driver.find_element_by_name('username')
    username.send_keys(os.environ['SCE_USERNAME'])
    password = driver.find_element_by_name('password')
    password.send_keys(os.environ['SCE_PASSWORD'])
    password.send_keys('\n')
    driver.find_element_by_id('searchMyAccounts')
    driver.get('https://www.sce.com/sma/ESCAA/EscGreenButtonData')
    time.sleep(2)
    for account in os.environ['SCE_ACCOUNTS'].split(' '):
        end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
        start_date = (datetime.date.today() - datetime.timedelta(days=6)).strftime('%m/%d/%Y')
        script = download_script % (account, start_date, end_date)
        response = driver.execute_script(script)
        with open(f'data/sce_{account}.xml', 'w') as data_file:
            data_file.write(response)


if __name__ == '__main__':
    main()
