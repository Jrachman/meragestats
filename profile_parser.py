from bs4 import BeautifulSoup
import csv
import time
import sel_linkedin
import credentials  # this is a module that I created in order to hold my credentials
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class wait_for_more_than_n_elements(object):
    def __init__(self, locator, count):
        self.locator = locator
        self.count = count

    def __call__(self, driver):
        try:
            count = len(EC._find_elements(driver, self.locator))
            print(count, self.count)
            return count > self.count
        except StaleElementReferenceException:
            return False


USER_EMAIL = credentials.GARRET_EMAIL
USER_PASSWORD = credentials.GARRET_PASSWORD


def urls_from_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.reader(f))


def soft_load_page(driver):
    path_to_company_cards = '//div[@class="pv-entity__logo company-logo"]'
    companies = driver.find_elements_by_xpath(path_to_company_cards)

    while True:
        elems = driver.find_elements_by_xpath('//button[@class="pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link"]')
        if not elems:
            break

        for e in elems:
            driver.execute_script("arguments[0].click();", e)
            time.sleep(1)

    wait = WebDriverWait(driver, 30)
    wait.until(wait_for_more_than_n_elements((By.XPATH, path_to_company_cards), len(companies)))


def get_profile_info(driver, profile_url):
    driver.get(f"{sel_linkedin.LINKEDIN_ROOT_URL}{profile_url}")

    # before we capture the soup, we need to do a couple of things first:
    #   - if the "Show n more experience(s)" button exists (if not, do nothing),
    #     click on button and repeat until the "Show fewer experiences" button shows
    #   - if the "Show n more role(s)" button exists (if not, do nothing),
    #     click on the button and repeat until the "Show fewer roles" button shows
    #
    # programming procedures:
    #   - find all buttons
    #   - if text matches
    #       (1) "Show n more experience(s)" or
    #       (2) "Show n more role(s)",
    #     click!
    #   - repeat the first step and if no buttons' text matches the 2 options,
    #     then SCOOP THE SOUP!

    soft_load_page(driver)
    reg_loaded_li_class = "pv-profile-section__sortable-card-item pv-profile-section pv-position-entity ember-view"
    soft_loaded_li_class = "pv-profile-section__card-item-v2 pv-profile-section pv-position-entity ember-view"
    soup = BeautifulSoup(driver.page_source, "html.parser")
    content_reg = soup.find_all("li", {"class": reg_loaded_li_class})
    content_soft = soup.find_all("li", {"class": soft_loaded_li_class})
    content = content_reg + content_soft
    print(content, len(content))
    print(content[0].prettify())

    for c in content:
        # there are 2 categories:
        #   (1) companies that have multiple positions
        #   (2) one to one, company to position

        if c.find_all("ul", {"class": "pv-entity__position-group mt2"}):
            print("this is (1)")
        else:
            print("this is (2)")


if __name__ == "__main__":
    list_of_urls_csv_format = urls_from_csv("merage_links.csv")
    driver = sel_linkedin.initialize_driver()
    sel_linkedin.login_linkedin(driver, USER_EMAIL, USER_PASSWORD)

    # for url in list_of_urls_csv_format:
    #     get_profile_info(driver, url[0])
    #     break

    get_profile_info(driver, "/in/katie-xiong/")

    driver.quit()
