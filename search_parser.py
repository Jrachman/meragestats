from bs4 import BeautifulSoup
import string
import time
import csv
import multiprocessing
import sel_linkedin
import credentials  # this is a module that I created in order to hold my credentials

PEOPLE_SEARCH_URL = f"{sel_linkedin.LINKEDIN_ROOT_URL}/search/results/people/?"


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
                if counter == 30:
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
    driver = sel_linkedin.initialize_driver()
    sel_linkedin.login_linkedin(driver, user_email, user_password)
    set_of_profiles = get_profile_urls_merage_page(driver, from_year, end_year)
    driver.quit()

    return set_of_profiles


def create_csv_from_set(set_of_profiles):
    with open("merage_links.csv", "w") as ml:
        cml = csv.writer(ml)
        for link in set_of_profiles:
            cml.writerow([link])


def gather_merage_profiles(multiple_at_once=False):
    arguments = (
        # (GARRET_EMAIL, GARRET_PASSWORD, 2008, 2010),
        (credentials.KATIE_EMAIL, credentials.KATIE_PASSWORD, 2008, 2009),
        (credentials.JULIAN_EMAIL, credentials.JULIAN_PASSWORD, 2010, 2012),
        (credentials.SALLY_EMAIL, credentials.SALLY_PASSWORD, 2013, 2016),
        (credentials.TOMMY_EMAIL, credentials.TOMMY_PASSWORD, 2017, 2019)
    )
    nresults = set()

    if multiple_at_once:
        with multiprocessing.Pool(processes=4) as pool:
            # running 4 accounts all at the same time does not perform well with the slow loading
            results = pool.starmap(run_merage_profile_parse, arguments)
            for result in results:
                nresults |= result
    else:
        for argument in arguments:
            nresults |= run_merage_profile_parse(*argument)

    return nresults


if __name__ == "__main__":
    final_set = gather_merage_profiles()
    print(final_set, len(final_set))

    create_csv_from_set(final_set)
