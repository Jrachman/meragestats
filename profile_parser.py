from bs4 import BeautifulSoup
import csv
import time
import sel_linkedin
import credentials  # this is a module that I created in order to hold my credentials

USER_EMAIL = credentials.GARRET_EMAIL
USER_PASSWORD = credentials.GARRET_PASSWORD


def urls_from_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.reader(f))


def soft_load_page(driver):
    while True:
        elems = driver.find_elements_by_xpath('//button[@class="pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link"]')
        if not elems:
            break

        for e in elems:
            driver.execute_script("arguments[0].click();", e)
            time.sleep(1)


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

    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.find_all("li", {"class": "pv-profile-section__sortable-card-item"})
    print(content)


if __name__ == "__main__":
    list_of_urls_csv_format = urls_from_csv("merage_links.csv")
    driver = sel_linkedin.initialize_driver()
    sel_linkedin.login_linkedin(driver, USER_EMAIL, USER_PASSWORD)

    # for url in list_of_urls_csv_format:
    #     get_profile_info(driver, url[0])
    #     break

    get_profile_info(driver, "/in/katie-xiong/")

    # driver.quit()
