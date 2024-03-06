import subprocess
import time

import pytest
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


@pytest.fixture(scope="module")
def app_url():
    # Start the Flask app
    flask_process = subprocess.Popen(
        ["python3", "-m", "flask", "--app", "app/flaskr", "run"]
    )
    # Wait for the app to start up
    time.sleep(2)
    app_url = "http://127.0.0.1:5000/"
    yield app_url
    # Shutdown the Flask app after all tests are finished
    flask_process.terminate()


@pytest.fixture(scope="module")
def driver():
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--width=2560")
    options.add_argument("--height=1440")
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(options=options, service=service)
    yield driver
    # Close the browser after all tests are finished
    driver.quit()


def test_home_page(app_url, driver):
    driver.get(app_url)
    assert "Lethologica" in driver.title


def test_easter_egg_not_initially_present(app_url, driver):
    driver.get(app_url)
    easter_egg = driver.find_element(By.CLASS_NAME, "cat")

    assert (
        easter_egg.value_of_css_property("display") == "none"
    ), "Easter egg appears before secret input"


def test_easter_egg_appears_after_correct_input(app_url, driver):
    driver.get(app_url)
    input_text_box = driver.find_element(By.ID, "def")
    input_text_box.send_keys("lethologicats")
    input_text_box.submit()

    easter_egg = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "cat"))
    )

    assert (
        easter_egg.value_of_css_property("display") == "block"
    ), "Easter egg did not appear after correct input"


def test_loader_not_initally_present(app_url, driver):
    driver.get(app_url)
    loader = driver.find_element(By.ID, "loader")

    assert (
        loader.value_of_css_property("display") == "none"
    ), "Loader appears before query is sent"


def test_loader_appears_after_input(app_url, driver):
    driver.get(app_url)
    input_text_box = driver.find_element(By.ID, "def")
    input_text_box.send_keys("test query")
    input_text_box.submit()

    loader = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loader"))
    )

    assert (
        loader.value_of_css_property("display") == "block"
    ), "Loader does not appear when query is sent"


def test_input_sanitised(app_url, driver):
    driver.get(app_url)
    input_text_box = driver.find_element(By.ID, "def")
    input_text_box.send_keys("<script></script>")
    input_text_box.submit()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element_value((By.ID, "def"), "")
    )

    assert input_text_box.get_attribute("value") == "", "Unsafe input is not sanitised"


def test_input_truncated(app_url, driver):
    driver.get(app_url)
    input_text_box = driver.find_element(By.ID, "def")
    input_text_box.send_keys(
        "A really long string of text that is surely going to be a malicious attacker who wants to spam out website and make the request take a really long time to encode and send and find a reverse dictionary for, which could potentially make our website hang and be vulnerable to DDOS attacks!"
    )
    input_text_box.submit()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element_value(
            (By.ID, "def"),
            "A really long string of text that is surely going to be a malicious attacker who wants to spam out website and make the ...",
        )
    )

    assert (
        input_text_box.get_attribute("value")
        == "A really long string of text that is surely going to be a malicious attacker who wants to spam out website and make the ..."
    ), "Long input is not truncated"


def test_credits_button(app_url, driver):
    driver.get(app_url)
    credits_btn = driver.find_element(By.ID, "creditsPopup")
    credits_btn.click()

    credits_popup = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "credits"))
    )

    assert (
        credits_popup.value_of_css_property("display") == "block"
    ), "Credits popup does not show correctly when clicked"

    close_credits_btn = driver.find_element(By.ID, "closeCreditsPopup")
    close_credits_btn.click()

    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.ID, "credits"))
    )


def test_about_button(app_url, driver):
    driver.get(app_url)

    about_btn = driver.find_element(By.ID, "aboutPopup")
    about_btn.click()

    about_popup = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "about"))
    )

    assert (
        about_popup.value_of_css_property("display") == "block"
    ), "About popup does not show correctly when clicked"

    close_about_btn = driver.find_element(By.ID, "closeAboutPopup")
    close_about_btn.click()

    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, "about")))
