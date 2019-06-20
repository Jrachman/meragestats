# import web driver
from selenium import webdriver
from bs4 import BeautifulSoup
import string
import time
import multiprocessing
from credentials import *  # this is a module that I created in order to hold my credentials

LINKEDIN_ROOT_URL = "https://www.linkedin.com"
PEOPLE_SEARCH_URL = f"{LINKEDIN_ROOT_URL}/search/results/people/?"


def initialize_driver():
    # specifies the path to the chromedriver.exe
    return webdriver.Chrome("./chromedriver")


def login_linkedin(driver, user_email, user_password):
    # driver.get method() will navigate to a page given by the URL address
    driver.get(f"{LINKEDIN_ROOT_URL}/uas/login?")

    # locate email form by_class_name
    username = driver.find_element_by_id("username")
    # send_keys() to simulate key strokes
    username.send_keys(user_email)

    # locate password form by_class_name
    password = driver.find_element_by_id("password")
    # send_keys() to simulate key strokes
    password.send_keys(user_password)
    # password.submit()

    # locate submit button by_class_name
    log_in_button = driver.find_element_by_xpath("//*[@id='app__container']/main/div/form/div[3]/button")
    # locate submit button by_class_id
    # log_in_button = driver.find_element_by_class_id('login submit-button')
    # locate submit button by_xpath
    # log_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    # .click() to mimic button click
    log_in_button.click()


def get_hrefs(driver, set_of_profiles):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return {link.get("href") for link in soup.find_all("a") if link.get("href") and "/in/" in link.get("href") and link.get("href") not in set_of_profiles}


def get_profile_urls(driver):
    set_of_profiles = set()

    for connection_level in ["F", "S", "O"]:
        for letter in string.ascii_lowercase:
            search_args = f'facetNetwork=%5B"{connection_level}"%5D&facetSchool=%5B%2217948%22%5D&keywords={letter}&origin=FACETED_SEARCH&page='

            for page_num in range(1, 101):
                driver.get(f"{PEOPLE_SEARCH_URL}{search_args}{page_num}")

                subset_of_profiles = get_hrefs(driver, set_of_profiles)
                if not subset_of_profiles:
                    break
                else:
                    set_of_profiles |= subset_of_profiles
                # instead of adding to a set, run the linkedin profile extracter
                # use linkedin username as unique identifier to eliminate the possibility of not being able to differentiate between two John Apple's
                print(f"current number of profiles captured: {len(set_of_profiles)}, CURRENT letter: {letter}")

            print(f"current number of profiles captured: {len(set_of_profiles)}, CURRENT letter (completed): {letter}")

        print(f"current number of profiles captured: {len(set_of_profiles)}, CURRENT connection level (completed): {connection_level}")

    print(set_of_profiles, len(set_of_profiles))
    # maybe push information to csv

    return set_of_profiles


def get_profile_urls_merage_page(driver, from_year, to_year):
    set_of_profiles = set()
    years = range(from_year, to_year + 1)

    prefix_url = "https://www.linkedin.com/school/uci-paul-merage-school-of-business/people/"

    for year in years:
        year_args = f"?educationEndYear={year}&educationStartYear={year}"
        driver.get(f"{prefix_url}{year_args}")

        SCROLL_PAUSE_TIME = 0.5
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        new_height = 0

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            counter = 0
            while new_height == last_height:
                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if counter == 20:
                    break
                else:
                    counter += 1

            if new_height == last_height:
                break
            last_height = new_height

        subset_of_profiles = get_hrefs(driver, set_of_profiles)
        set_of_profiles |= subset_of_profiles
        print(f"subset: {len(subset_of_profiles)}", f"set: {len(set_of_profiles)}")

    return set_of_profiles


def run_merage_profile_parse(user_email, user_password, from_year, end_year):
    driver = initialize_driver()
    login_linkedin(driver, user_email, user_password)
    set_of_profiles = get_profile_urls_merage_page(driver, from_year, end_year)
    driver.quit()

    return set_of_profiles


def multiprocess_gather_merage_profiles():
    arguments = (
        (GARRET_EMAIL, GARRET_PASSWORD, 2008, 2012),
        (JULIAN_EMAIL, JULIAN_PASSWORD, 2013, 2015),
        (KATIE_EMAIL, KATIE_PASSWORD, 2016, 2019),
    )
    p = multiprocessing.Process(target=run_merage_profile_parse, args=arguments)
    p.start()
    p.join()


if __name__ == "__main__":
    final_set = multiprocess_gather_merage_profiles()
    print(final_set, len(final_set))
