import os
import time

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
    # serviceAccountNumber: 51819453 & 51819495
    script = download_script % ('51819495', '05/07/20', '05/13/20')
    response = driver.execute_script(script)
    with open('data.xml', 'w') as data_file:
        data_file.write(response)
    pass


if __name__ == '__main__':
    main()
