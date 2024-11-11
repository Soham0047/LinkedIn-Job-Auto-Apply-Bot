from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Replace with your credentials and information
ACCOUNT_EMAIL = "XXX@abc.com"
ACCOUNT_PASSWORD = "YOUR_PASSWORD"
PHONE = "1234567890"


# Function to abort the application if it is too complex
def abort_application(driver):
    try:
        # Click the 'Close' button
        close_button = driver.find_element(by=By.CLASS_NAME, value="artdeco-modal__dismiss")
        close_button.click()

        time.sleep(2)

        # Click the 'Discard' button to confirm closing the application
        discard_buttons = driver.find_elements(by=By.CLASS_NAME, value="artdeco-modal__confirm-dialog-btn")
        if discard_buttons:
            discard_buttons[-1].click()  # Clicks the last discard button found
        print("Application aborted.")
    except NoSuchElementException:
        print("Error while trying to abort the application. Element not found.")
    except ElementNotInteractableException:
        print("Error: Element was not interactable while trying to abort.")


# Set up the Chrome options to keep the browser open
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()  # Ensures better visibility for element interaction

# Navigate to the LinkedIn job search page
driver.get("ENTER_JOB_LINK")

# Wait for the page to load and check for the 'Reject Cookies' button
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    cookies_buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
    for button in cookies_buttons:
        if 'reject' in button.text.lower() or 'deny' in button.text.lower():
            button.click()
            print("Cookies rejected.")
            break
except TimeoutException:
    print("No 'Reject Cookies' button found or not clickable.")

# Click the 'Sign in' button
try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign in"))).click()
except TimeoutException:
    print("Sign-in button not found.")

# Enter login credentials
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(ACCOUNT_EMAIL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(ACCOUNT_PASSWORD)
    password_field = driver.find_element(by=By.ID, value="password")
    password_field.send_keys(Keys.ENTER)
    print("Logged in.")
except TimeoutException:
    print("Login fields not found.")

# Manually solve CAPTCHA if necessary
input("Press Enter after you have solved the CAPTCHA.")

# Wait for job listings to load
time.sleep(5)
all_listings = driver.find_elements(by=By.CSS_SELECTOR, value=".job-card-container--clickable")
print(f"Found {len(all_listings)} job listings.")

# Iterate over job listings and attempt to apply
for listing in all_listings:
    print("Opening job listing.")
    listing.click()
    time.sleep(2)  # Give time for the job detail page to load

    try:
        # Locate and click the 'Apply' button
        apply_button = driver.find_element(by=By.CSS_SELECTOR, value=".jobs-s-apply button")
        apply_button.click()
        print("Apply button clicked.")

        # Wait for phone input field and fill in the phone number
        time.sleep(3)  # Wait for the application modal to load
        phone_input = driver.find_element(by=By.CSS_SELECTOR, value="input[id*=phoneNumber]")
        if phone_input and phone_input.get_attribute("value") == "":
            phone_input.send_keys(PHONE)

        # Check if a 'Continue' or 'Submit' button is present
        submit_button = driver.find_element(by=By.CSS_SELECTOR, value="footer button")
        if submit_button.get_attribute("data-control-name") == "continue_unify":
            abort_application(driver)
            print("Complex application form detected. Application skipped.")
            continue
        else:
            submit_button.click()
            print("Application submitted.")

        time.sleep(2)  # Wait for the submission to complete

        # Close the confirmation modal
        close_button = driver.find_element(by=By.CLASS_NAME, value="artdeco-modal__dismiss")
        close_button.click()

    except NoSuchElementException:
        print("No apply button or issue with applying for this job. Skipping.")
        continue

# End the WebDriver session
time.sleep(5)
driver.quit()
print("All processes completed. Browser closed.")
