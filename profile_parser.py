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

# need to gather
#   - comapny name / company url
#   - position(s) / duration of time
# format: [company name, company url, position, duration of time]


def get_info_multiple_positions_to_company(driver, user_name, content):
    profile_info = []

    company_name = content.find("h3", {"class": "t-16 t-black t-bold"}).text[14:-1]
    company_url = content.find("a", {"data-control-name": "background_details_company"}).get("href")
    company_info = [[company_name, company_url]]

    positions = [c.text[7:-1] for c in content.find_all("h3", {"class": "t-14 t-black t-bold"})]
    durations = [c.text[16:-1] for c in content.find_all("h4", {"class": "pv-entity__date-range t-14 t-black t-normal"})]
    for p, d in zip(positions, durations):
        profile_info.append([user_name, company_name, p, d])

    return company_info, profile_info


def get_info_single_position_to_company(driver, user_name, content):
    company_name = content.find("h4", {"class": "t-16 t-black t-normal"}).text[14:-1]
    company_url = content.find("a", {"data-control-name": "background_details_company"}).get("href")
    company_info = [[company_name, company_url]]

    position = content.find("h3", {"class": "t-16 t-black t-bold"}).text
    duration = content.find("h4", {"class": "pv-entity__date-range t-14 t-black--light t-normal"}).text[16:-1]

    return company_info, [[user_name, company_name, position, duration]]


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

    user_name = soup.find("li", {"class": "inline t-24 t-black t-normal break-words"}).text[13:-11]
    content_reg = soup.find_all("li", {"class": reg_loaded_li_class})
    content_soft = soup.find_all("li", {"class": soft_loaded_li_class})
    content = content_reg + content_soft

    company_dir = []
    profile_dir = []
    for c in content:
        # there are 2 categories:
        #   (1) companies that have multiple positions
        #   (2) one to one, company to position

        if c.find_all("ul", {"class": "pv-entity__position-group mt2"}):
            # (1)
            company_info, profile_info = get_info_multiple_positions_to_company(driver, user_name, c)
            company_dir += company_info
            profile_dir += profile_info
        else:
            # (2)
            company_info, profile_info = get_info_single_position_to_company(driver, user_name, c)
            company_dir += company_info
            profile_dir += profile_info

    print('\n'.join('{}: {}'.format(*k) for k in enumerate(company_dir)))
    print('\n'.join('{}: {}'.format(*k) for k in enumerate(profile_dir)))


if __name__ == "__main__":
    list_of_urls_csv_format = urls_from_csv("merage_links.csv")
    driver = sel_linkedin.initialize_driver()
    sel_linkedin.login_linkedin(driver, USER_EMAIL, USER_PASSWORD)

    # for url in list_of_urls_csv_format:
    #     get_profile_info(driver, url[0])
    #     break

    get_profile_info(driver, "/in/katie-xiong/")

    driver.quit()
