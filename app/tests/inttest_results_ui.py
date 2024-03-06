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
    try:
        # Wait for the app to start up
        time.sleep(2)
        app_url = "http://127.0.0.1:5000/"
        yield app_url
    finally:
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


# Automatically invoke and reuse result across tests
@pytest.fixture(scope="module")
def results_driver(app_url, driver):
    # Returns driver after inputting a valid query
    driver.get(app_url)
    input_text_box = driver.find_element(By.ID, "def")
    input_text_box.send_keys("A valid definition")
    input_text_box.submit()

    # Wait up to 30 seconds for results to be returned
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "def_card"))
    )
    # Wait for loader to disappear
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "loader"))
    )

    yield driver


def test_valid_input_returns_results(results_driver):
    def_cards = results_driver.find_elements(By.CLASS_NAME, "def_card")
    assert len(def_cards) > 0, "No results returned for valid input"


def test_click_to_open_definition(results_driver):
    def_card = results_driver.find_element(By.CLASS_NAME, "def_card")
    definition = results_driver.find_element(By.CLASS_NAME, "definition")
    assert not definition.is_displayed(), "Definition is shown before card is clicked"

    def_card.click()

    try:
        # Wait for the definition to open after clicking
        WebDriverWait(results_driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "definition"))
        )
        assert (
            definition.is_displayed()
        ), "Definition does not show when card is clicked"
    finally:
        # Reset state
        def_card.click()


def test_click_explore(results_driver):
    def_card = results_driver.find_element(By.CLASS_NAME, "def_card")
    def_card.click()

    try:
        # Wait for explore icon to become clickable after toggling definition
        WebDriverWait(results_driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "explore-button"))
        ).click()

        definition = results_driver.find_element(By.CLASS_NAME, "def-item").text
        input_text_box = results_driver.find_element(By.ID, "def")
        # Check that input text matches subset of definition text (exclude added punctuation)
        assert (
            input_text_box.get_attribute("value") in definition
        ), "Clicking explore does not load definition into input box"
    finally:
        # Reset state
        def_card.click()


def test_click_filter_changes_display(results_driver):
    noun_cards = results_driver.find_elements(
        By.XPATH, "//li[contains(@class, 'def_card') and contains(., '(noun)')]"
    )
    assert len(noun_cards) > 0, "Expected nouns but none found in results"

    # Click to filter out nouns
    noun_filter = results_driver.find_element(
        By.XPATH, "//div[@class='filter']/label[@for='show_noun']"
    )
    noun_filter.click()

    try:
        # Check that noun cards disappear
        WebDriverWait(results_driver, 5).until(
            EC.invisibility_of_element(noun_cards[0])
        )
        noun_card_after_filter = results_driver.find_elements(
            By.XPATH, "//li[contains(@class, 'def_card') and contains(., '(noun)')]"
        )
        for card in noun_card_after_filter:
            assert not card.is_displayed(), "Unexpected noun shown in filtered results"
    finally:
        # Reset state
        noun_filter.click()


def test_click_show_more_reveals_more_definitions(results_driver):
    def_cards = results_driver.find_elements(By.CLASS_NAME, "def_card")
    visible_def_cards = [c for c in def_cards if c.is_displayed()]
    original_num_def_cards = len(visible_def_cards)
    assert original_num_def_cards > 0, "No results originally returned"

    # Click show more button
    WebDriverWait(results_driver, 10).until(
        EC.element_to_be_clickable((By.ID, "show_more"))
    ).click()

    new_def_cards = WebDriverWait(results_driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "def_card"))
    )
    new_visible_def_cards = [c for c in new_def_cards if c.is_displayed()]
    assert (
        len(new_visible_def_cards) > original_num_def_cards
    ), "Show more button does not show more results"
