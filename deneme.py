from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import io
from datetime import datetime

class TrendyolScraper:
    def __init__(self, product_url):
        self.product_url = product_url
        self.comments = []
        self.driver = self.setup_selenium()

    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Headless modda çalıştır
        service = Service('C:/chrome/chromedriver-win64/chromedriver.exe')  # ChromeDriver yolunu belirtin
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def scroll_page(self):
        self.get_comments_from_soup()  # Scroll başlamadan önce ilk yorumları çek
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        counter = 1  # Sayaç başlangıcı
        while True:
            print(f"Taranıyor ({counter})")  # Döngü her çalıştığında sayacın değerini yazdır
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            start_time = datetime.now()
            print(f"Start waiting at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(5)  # Sayfanın yüklenmesi için bekle
            end_time = datetime.now()
            print(f"End waiting at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            print(f"last_height: {last_height}, new_height: {new_height}")  # Yükseklik değerlerini yazdır
            self.get_comments_from_soup()  # Her döngüden sonra yorumları tekrar çek
            
            try:
                load_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more-button"))
                )
                load_more_button.click()
            except:
                pass
            
            if new_height == last_height:
                break  # Eğer yükseklik değişmediyse döngüden çık
            last_height = new_height
            counter += 1  # Sayaç her döngüde bir artar

    def get_comments_from_soup(self):
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        comment_elements = soup.select("div.comment div.comment-text")
        for element in comment_elements:
            comment_text = element.get_text(strip=True)
            if {'comment': comment_text} not in self.comments:
                self.comments.append({'comment': comment_text})

    def get_comments(self):
        print("Scraping comments...")
        self.driver.get(self.product_url)
        self.scroll_page()
        return self.comments

    def close(self):
        self.driver.quit()

if __name__ == '__main__':
    product_url = "https://www.trendyol.com/mahmood/cappuccino-cikolata-parcacikli-25gr-x-20-adet-p-39723920/yorumlar?boutiqueId=61&merchantId=686009"
    scraper = TrendyolScraper(product_url)
    data = scraper.get_comments()
    scraper.close()

    # Dosyaya yazma işlemi
    output_file = "comments_output.txt"
    with io.open(output_file, 'w', encoding='utf-8') as file:
        for comment in data:
            file.write(f"Comment: {comment['comment']}\n")
            file.write("--------------------\n")

    print(f"Scraping completed. {len(data)} comments were scraped and saved to {output_file}")
