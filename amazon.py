import time
import requests
from bs4 import BeautifulSoup
import mysql.connector as db
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
failed = []


class amazon():
    def __init__(self, zipcode):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": '',
            "database": "amazon_scrap"
        }

        self.ss = requests.Session()
        self.zipcode = zipcode

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        options.add_argument("--incognito")
        self.driver = webdriver.Chrome(
            executable_path='./chromedriver', chrome_options=options)

        self.driver.get('https://www.amazon.com/')
        wait = WebDriverWait(self.driver, 40)
        wait.until(EC.presence_of_element_located((By.ID, 'nav-logo-sprites')))
        self.driver.find_element_by_xpath(
            '//a[@id="nav-global-location-popover-link"]').click()
        time.sleep(2)

        self.driver.find_element_by_xpath(
            '//input[@id="GLUXZipUpdateInput"]').send_keys(self.zipcode)
        time.sleep(2)
        self.driver.find_element_by_xpath(
            '//span[@id="GLUXZipUpdate"]').click()
        time.sleep(3)
        self.driver.find_element_by_xpath(
            '//*[@id="a-popover-3"]/div/div[2]/span').click()
        time.sleep(5)

    def scrap_data(self, asin):
        self.asin = asin

        self.driver.get(
            'https://www.amazon.com/dp/{asin}'.format(asin=self.asin['asin']))
        try:
            self.iframe1 = self.driver.find_element_by_xpath(
                '//*[@id="ape_Detail_hero-quick-promo_Desktop_iframe"]')
        except:
            self.iframe1 = ''
        try:
            self.iframe2 = self.driver.find_element_by_xpath(
                '//*[@id="ape_Detail_ams-detail-right-v2_desktop_iframe"]')
        except:
            self.iframe2 = ''

        return [self.iframe1, self.iframe2]

    def clean_data(self, data):
        save_data = []
        for iframe in data:
            if iframe != '':
                time.sleep(1)
                pr_type = json.loads(iframe.get_attribute('name'))['slotName']
                self.driver.switch_to.frame(iframe)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'

                }
                try:
                    open_request = requests.get(self.driver.find_element_by_xpath(
                        '//*[@id="sp_hqp_shared_inner"]/a').get_attribute('href'), headers=headers)
                except:
                    open_request = requests.get(self.driver.find_element_by_xpath(
                        '//*[@id="ad"]/div/div/div/a').get_attribute('href'), headers=headers)

                soup = BeautifulSoup(open_request.text, 'html.parser')
                if 'Enter the characters you see below' not in open_request.text:
                    title = soup.find(
                        'span', {'id': 'productTitle'}).text.replace('\n', '')
                    image = soup.find('img', {'id': 'landingImage'})['src']
                    rating = soup.find(
                        'i', {'class': 'a-icon-star'}).text.split(' ')[0]
                    review_count = soup.find('span', {'id': 'acrCustomerReviewText'}).text.split(
                        ' ')[0].replace(',', '')
                    try:
                        price = self.driver.find_element_by_xpath(
                            '//*[@id="ad"]/div/div/div/div[2]/div/div[2]/div/div/div/span[1]/span[2]').text.replace('$', '')
                    except:
                        price = self.driver.find_element_by_xpath(
                            '//*[@id="sp_hqp_shared"]/div/div[3]/div[2]/span[2]').text.replace('$', '')
                    brand_list = ['Nutramigen', 'Neuriva', 'Enfamil', 'K-Y', 'Mucinex', 'Airborne', 'Bodi-Ome', 'Amope', 'PurAmino', 'Move Free', 'Lanacane', 'MegaRed',
                                  'Digestive Advantage', 'Clearasil', 'Enfagrow', 'Delsym', 'Enspire', 'Durex', 'Schiff', 'Veet', 'Cepacol', 'LiceMD', 'Enfasmart', 'Scalpicin', 'Other MJN']
                    brand_status = any(brand in title for brand in brand_list)
                    save_data.append((self.asin['flag'], self.asin['asin'], pr_type,
                                      title, image, rating, review_count, price, brand_status))
                    self.driver.switch_to.default_content()
                else:
                    failed.append(self.asin)
                time.sleep(2)
            else:
                save_data.append((self.asin['flag'], self.asin['asin'], None,
                                  None, None, None, None, None, None))
        return save_data

    def store_data(self, data):
        conn = db.connect(**self.config)
        conn.autocommit = True
        mycursor = conn.cursor()
        mycursor.executemany(
            "insert into ads_data (flag,asin,product_type,title,image,rating,review_count,price,brand_status) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)", data)
        conn.commit()
        mycursor.close()
        conn.close()


if __name__ == "__main__":
    t = amazon('07054')
    asin_value = [{'asin': 'B08836KTVQ', 'flag': '1'}, {'asin': 'B005LEMQOS', 'flag': '1'}, {'asin': 'B0057UUGRU', 'flag': '1'}, {'asin': 'B01AAQD2NU', 'flag': '1'}, {'asin': 'B079Y7KTDN', 'flag': '1'}, {'asin': 'B0057UUHGU', 'flag': '1'}, {'asin': 'B01K5S5KWE', 'flag': '1'}, {'asin': 'B079C81WDS', 'flag': '2'}, {'asin': 'B07HDVFLKX', 'flag': '2'}, {'asin': 'B0046KI188', 'flag': '2'}, {'asin': 'B00EFRVDQ4', 'flag': '2'}, {'asin': 'B000083JX0', 'flag': '2'}, {'asin': 'B01G7MXO9I', 'flag': '2'}, {'asin': 'B07BDPKJ2Q', 'flag': '2'}, {'asin': 'B000V83X5U', 'flag': '2'}, {'asin': 'B00K3EM2AE', 'flag': '2'}, {'asin': 'B008IYDYXU', 'flag': '2'}, {'asin': 'B0882X68CG', 'flag': '2'}, {'asin': 'B08835V9NW', 'flag': '2'}, {'asin': 'B00U2WEJE4', 'flag': '2'}, {'asin': 'B008IYDYSA', 'flag': '2'}, {'asin': 'B00LE99PA2', 'flag': '3'}, {'asin': 'B009LZHMCO', 'flag': '3'}, {'asin': 'B0057UUGSO', 'flag': '3'}, {'asin': 'B000ALB4H2', 'flag': '3'}, {'asin': 'B000ALB4GS', 'flag': '3'}, {'asin': 'B00VHPJSZ0', 'flag': '3'}, {'asin': 'B00EFRV7Y2', 'flag': '3'}, {'asin': 'B01DBY8P8U', 'flag': '3'}, {'asin': 'B00LZUZ5Z4', 'flag': '3'}, {'asin': 'B08831425S', 'flag': '2'}, {'asin': 'B0882NYYW3', 'flag': '3'}, {'asin': 'B0882W8BWC', 'flag': '3'}, {'asin': 'B08836KTVP', 'flag': '3'}, {'asin': 'B017YWRVT4', 'flag': '3'}, {'asin': 'B0759N57BX', 'flag': '3'}, {
        'asin': 'B071Z8NH6F', 'flag': '3'}, {'asin': 'B077T2SKYT', 'flag': '5'}, {'asin': 'B071S7TS1Z', 'flag': '5'}, {'asin': 'B002T5L454', 'flag': '5'}, {'asin': 'B001KYPZ4G', 'flag': '3'}, {'asin': 'B0070YFJGO', 'flag': '5'}, {'asin': 'B0070YFJKK', 'flag': '5'}, {'asin': 'B00B29WMIQ', 'flag': '5'}, {'asin': 'B00U2VYOSG', 'flag': '5'}, {'asin': 'B01E97PJ8M', 'flag': '5'}, {'asin': 'B006GA45G8', 'flag': '3'}, {'asin': 'B00GUFUW1G', 'flag': '5'}, {'asin': 'B00GUFUVX0', 'flag': '5'}, {'asin': 'B0010Y5EV0', 'flag': '5'}, {'asin': 'B07RHMHB34', 'flag': '4'}, {'asin': 'B07RP8PGCC', 'flag': '4'}, {'asin': 'B07VLN8RKB', 'flag': '4'}, {'asin': 'B07VLK2ZMT', 'flag': '4'}, {'asin': 'B07VLK331W', 'flag': '4'}, {'asin': 'B07VSVMF9H', 'flag': '4'}, {'asin': 'B07VPS6NBH', 'flag': '4'}, {'asin': 'B07VS3VGMZ', 'flag': '4'}, {'asin': 'B07VSVC1C7', 'flag': '4'}, {'asin': 'B07VNPJGC4', 'flag': '4'}, {'asin': 'B07R7XLKMZ', 'flag': '4'}, {'asin': 'B00XQFJXK4', 'flag': '4'}, {'asin': 'B07Z6RRHV4', 'flag': '5'}, {'asin': 'B07Z6RSXWR', 'flag': '5'}, {'asin': 'B084DPVXDG', 'flag': '5'}, {'asin': 'B08618ZMDB', 'flag': '5'}, {'asin': 'B086194JZ2', 'flag': '3'}, {'asin': 'B08G6KD15Z', 'flag': '3'}, {'asin': 'B08GKYNQJX', 'flag': '5'}, {'asin': 'B08G9FX8DG', 'flag': '5'}, {'asin': 'B08GKXHQKN', 'flag': '3'}, {'asin': 'B08LDPR3YH', 'flag': '3'}]
    for asin in asin_value:
        scrap = t.scrap_data(asin)
        clean = t.clean_data(scrap)
        t.store_data(clean)

with open('failed.txt', 'w+') as w:
    aa = str(failed)
    w.write(aa)
