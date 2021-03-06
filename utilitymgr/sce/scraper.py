import os
import time

from selenium import webdriver

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
    username = driver.find_element_by_name('username')
    username.send_keys(os.environ['SCE_USERNAME'])
    password = driver.find_element_by_name('password')
    password.send_keys(os.environ['SCE_PASSWORD'])
    password.send_keys('\n')
    driver.find_element_by_id('searchMyAccounts')
    driver.get('https://www.sce.com/sma/ESCAA/EscGreenButtonData')
    time.sleep(2)
    for account in os.environ['SCE_ACCOUNTS'].split(' '):
        start_date, end_date = map(lambda x: x.strftime('%m/%d/%y'), utils.week_start_end())
        script = download_script % (account, start_date, end_date)
        response = driver.execute_script(script)
        with open(f'data/sce_{account}.xml', 'w') as data_file:
            data_file.write(response)


if __name__ == '__main__':
    main()
