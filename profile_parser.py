from bs4 import BeautifulSoup
import csv
import sel_linkedin
import credentials  # this is a module that I created in order to hold my credentials

USER_EMAIL = credentials.JULIAN_EMAIL
USER_PASSWORD = credentials.JULIAN_PASSWORD
LINKEDIN_ROOT_URL = "https://www.linkedin.com"


def urls_from_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.reader(f))


def get_profile_info(driver, profile_url):
    driver.get(f"{sel_linkedin.LINKEDIN_ROOT_URL}{profile_url}")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.find("section", {"id": "experience-section"})
    print(content.prettify())


if __name__ == "__main__":
    list_of_urls_csv_format = urls_from_csv("merage_links.csv")
    driver = sel_linkedin.initialize_driver()
    sel_linkedin.login_linkedin(driver, USER_EMAIL, USER_PASSWORD)

    for url in list_of_urls_csv_format:
        get_profile_info(driver, url[0])
        break

    driver.quit()
