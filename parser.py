# import web driver
from selenium import webdriver
from bs4 import BeautifulSoup

user_email = "put email here"
user_password = "put password here"

# specifies the path to the chromedriver.exe
driver = webdriver.Chrome("./chromedriver")

# driver.get method() will navigate to a page given by the URL address
driver.get("https://www.linkedin.com/uas/login?")

# locate email form by_class_name
username = driver.find_element_by_id("username")

# send_keys() to simulate key strokes
username.send_keys(user_email)

# locate password form by_class_name
password = driver.find_element_by_id("password")

# send_keys() to simulate key strokes
password.send_keys(user_password)

# locate submit button by_class_name
log_in_button = driver.find_element_by_xpath("//*[@id='app__container']/main/div/form/div[3]/button")

# locate submit button by_class_id
# log_in_button = driver.find_element_by_class_id('login submit-button')

# locate submit button by_xpath
# log_in_button = driver.find_element_by_xpath('//*[@type="submit"]')

# .click() to mimic button click
log_in_button.click()
merage_search_url = "https://www.linkedin.com/search/results/people/?facetSchool=%5B%2217948%22%5D&origin=FACETED_SEARCH&page="

set_of_profiles = set()

for page_num in range(1, 101):
    driver.get(f"{merage_search_url}{page_num}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    for link in soup.find_all("a"):
        profile_url = link.get("href")
        if "/in/" in profile_url and profile_url not in set_of_profiles:
            print(profile_url)
            set_of_profiles.add(profile_url)

print(set_of_profiles, len(set_of_profiles))
# maybe push information to csv
