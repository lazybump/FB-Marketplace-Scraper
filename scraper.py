from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd

# My credentials
print(
    "Hey! We will be accessing facebook's website, but first we need some credentials"
)
my_email = input("Facebook login email: ")
my_password = input("Facebook login password: ")

chrome_options = Options()
my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={my_user_agent}")
chrome_options.add_argument("--disable-notifications")

driver = webdriver.Chrome(
    "C:\Program Files (x86)\chromedriver.exe", options=chrome_options
)
driver.get("https://www.facebook.com/marketplace/?ref=app_tab")
driver.maximize_window()

try:
    # Wait for cookie prompt before rejecting cookies
    decline_cookies_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(text(), "Decline optional cookies")]')
        )
    )
    decline_cookies_btn.click()
except:
    pass

# Log in with credentials
email_field = driver.find_element(By.ID, "email")
email_field.clear()
email_field.send_keys(my_email)
password_field = driver.find_element(By.ID, "pass")
password_field.clear()
password_field.send_keys(my_password)
password_field.submit()

# Decide what to search for
search_box = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search Marketplace"]'))
)
search_box.send_keys("car")
search_box.send_keys(Keys.ENTER)

time.sleep(3)

total_listings = 0
scroll_count = 0
max_scrolls = 3
titles = []
prices = []
links = []
images = []

while scroll_count < max_scrolls:
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait for new listings to load
    time.sleep(3)
    # Update the soup with the new page source
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find the new listings
    listings_container = soup.find("div", {"role": "main"})

    new_listings = listings_container.find_all(
        "a", href=lambda href: href.startswith("/marketplace/item")
    )[total_listings:]

    # Check if new listings have been loaded
    if len(new_listings) > 0:
        # Scrape listing data, and append to respective lists
        for listing in new_listings:
            try:
                title = listing.find("span", style=re.compile("webkit"))
                titles.append(title.text if title else None)
                price = listing.find("span", string=re.compile("^£"))
                prices.append(price.text if price else None)
                link = listing["href"]
                links.append(link if link else None)
                image = listing.find("img")["src"]
                images.append(image if image else None)
            except Exception:
                print(Exception)
        # Update the total number of listings
        total_listings += len(new_listings)
        scroll_count += 1
    else:
        # No new listings loaded, exit the while loop
        break


# Create the DataFrame
data = {"Title": titles, "Price": prices, "Link": links, "Image": images}
df = pd.DataFrame(data)
# Clean the data up a little
df.Price = df.Price.str.replace("£", "")
df.Link = "https://www.facebook.com" + df.Link

# df.to_csv("facebook_listings.csv")

df_trunc = df.head(20)
df_trunc.to_csv("facebook_car_listings.csv", index=False)
