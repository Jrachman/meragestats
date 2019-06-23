from selenium import webdriver

LINKEDIN_ROOT_URL = "https://www.linkedin.com"


def initialize_driver():
    return webdriver.Chrome("./chromedriver")


def login_linkedin(driver, user_email, user_password):
    driver.get(f"{LINKEDIN_ROOT_URL}/uas/login?")

    username = driver.find_element_by_id("username")
    username.send_keys(user_email)

    password = driver.find_element_by_id("password")
    password.send_keys(user_password)
    # password.submit()

    log_in_button = driver.find_element_by_xpath("//*[@id='app__container']/main/div/form/div[3]/button")
    log_in_button.click()
