# import web driver
from selenium import webdriver
from bs4 import BeautifulSoup

USER_EMAIL = "katiexiong1998@hotmail.com"
USER_PASSWORD = "PaulMerage123"
LINKEDIN_ROOT_URL = "https://www.linkedin.com"


def initialize_driver():
    # specifies the path to the chromedriver.exe
    return webdriver.Chrome("./chromedriver")


def login_linkedin(driver):
    # driver.get method() will navigate to a page given by the URL address
    driver.get("https://www.linkedin.com/uas/login?")

    # locate email form by_class_name
    username = driver.find_element_by_id("username")
    # send_keys() to simulate key strokes
    username.send_keys(USER_EMAIL)

    # locate password form by_class_name
    password = driver.find_element_by_id("password")
    # send_keys() to simulate key strokes
    password.send_keys(USER_PASSWORD)

    # locate submit button by_class_name
    log_in_button = driver.find_element_by_xpath("//*[@id='app__container']/main/div/form/div[3]/button")
    # locate submit button by_class_id
    # log_in_button = driver.find_element_by_class_id('login submit-button')
    # locate submit button by_xpath
    # log_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    # .click() to mimic button click
    log_in_button.click()


def get_profile_urls(driver):
    merage_search_url = f"{LINKEDIN_ROOT_URL}/search/results/people/?facetSchool=%5B%2217948%22%5D&origin=FACETED_SEARCH&page="

    set_of_profiles = set()
    for page_num in range(1, 101):
        driver.get(f"{merage_search_url}{page_num}")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for link in soup.find_all("a"):
            profile_url = link.get("href")
            if "/in/" in profile_url and profile_url not in set_of_profiles:
                print(profile_url)
                set_of_profiles.add(profile_url)
                # instead of adding to a set, run the linkedin profile extracter
                # use linkedin username as unique identifier to eliminate the possibility of not being able to differentiate between two John Apple's

    print(set_of_profiles, len(set_of_profiles))
    # maybe push information to csv
    return set_of_profiles


if __name__ == "__main__":
    driver = initialize_driver()
    login_linkedin(driver)
    set_of_profiles = get_profile_urls(driver)
