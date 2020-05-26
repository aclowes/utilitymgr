import os
import datetime

from selenium import webdriver

download_script = """
var response = await fetch('%s');
return await response.text();
"""


def main():
    driver = webdriver.Chrome('./chromedriver')
    driver.implicitly_wait(10)  # seconds
    driver.get('https://my.luxproducts.com/connect/login.html')
    username = driver.find_element_by_name('username')
    username.send_keys(os.environ['LUX_USERNAME'])
    password = driver.find_element_by_name('password')
    password.send_keys(os.environ['LUX_PASSWORD'])
    password.send_keys('\n')
    driver.find_element_by_id('tstats')
    start = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    for thermostat in os.environ['LUX_THERMOSTATS'].split(' '):
        base_url = ('https://my.luxproducts.com/connect/rest/gateways/'
                    f'{thermostat}/usage?bucket-size=PT60M&duration=P7D&day={start}')
        script = download_script % base_url
        response = driver.execute_script(script)
        with open(f'data/lux_{thermostat}.json', 'w') as data_file:
            data_file.write(response)


if __name__ == '__main__':
    main()
