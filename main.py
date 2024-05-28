import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from notion_client import Client
import pytesseract
from PIL import Image
import cv2
from dotenv import load_dotenv
import pyautogui

# Load environment variables from .env file
load_dotenv()

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {message}")


# Read Notion API key, page ID, email, and password from environment variables
notion_api_key = os.getenv('NOTION_API_KEY_My_Selenium_Notion_Integration')
notion_page_id = os.getenv('NOTION_PAGE_ID_My_Selenium_Notion_Integration')
apple_email = os.getenv('APPLE_EMAIL')
apple_password = os.getenv('APPLE_PASSWORD')

# Debug prints to check if environment variables are being retrieved correctly
log_message(f"Notion API Key: {notion_api_key}")
log_message(f"Notion Page ID: {notion_page_id}")
log_message(f"Apple Email: {apple_email}")

if not notion_api_key or not notion_page_id or not apple_email or not apple_password:
    raise ValueError(
        "Environment variables NOTION_API_KEY, NOTION_PAGE_ID, APPLE_EMAIL, and APPLE_PASSWORD must be set")

# Initialize Notion client
notion = Client(auth=notion_api_key)


def test_integration_access():
    try:
        # Fetch the page
        page = notion.pages.retrieve(page_id=notion_page_id)
        log_message(f"Integration access confirmed. \nPage data: {page}")

        # Check if the page has a title
        if 'properties' in page and 'title' in page['properties']:
            title_property = page['properties']['title']
            if title_property['type'] == 'title' and title_property['title']:
                log_message(f"Page title: {title_property['title'][0]['text']['content']}")
            else:
                log_message("Page has no title or title format is unexpected")
        else:
            log_message("Page properties do not include a title")
    except Exception as e:
        log_message(f"Failed to access page: {e}")


test_integration_access()

# Selenium setup
options = Options()
options.add_experimental_option("detach", True)
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Hardcoded path for testing
chromedriver_path = "D:\\D-H4wk Downloads and Installations\\Software Installations\\Chrome Web Driver\\Webdriver 125\\chromedriver-win64\\chromedriver.exe"

# Use the hardcoded path to the manually downloaded ChromeDriver
try:
    log_message(f"Attempting to initialize ChromeDriver with path: {chromedriver_path}")
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    log_message("ChromeDriver initialized successfully.")
except Exception as e:
    log_message(f"Failed to initialize ChromeDriver: {e}")
    raise


def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def locate_text_position(text, full_image_path):
    image = cv2.imread(full_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(binary_image, config=custom_config, output_type=pytesseract.Output.DICT)

    for i, text_detected in enumerate(details['text']):
        if text in text_detected:
            (x, y, w, h) = (details['left'][i], details['top'][i], details['width'][i], details['height'][i])
            return (x, y, w, h)
    return None


def click_text_position(text, image_path):
    position = locate_text_position(text, image_path)
    if position:
        x, y, w, h = position
        log_message(f"Located position of '{text}': {position}")
        # Simulate clicking the element using pyautogui
        pyautogui.click(x + w / 2, y + h / 2)
        return True
    else:
        log_message(f"Failed to locate '{text}' on the screen.")
        return False


def find_and_click_apple_button():
    screenshot_path = "notion_login_page.png"
    driver.save_screenshot(screenshot_path)

    if click_text_position('Continue with Apple', screenshot_path):
        return True

    log_message("Failed to click 'Continue with Apple' button using text recognition.")
    return False


def login_to_notion_with_apple():
    log_message("Navigating to Notion login page.")
    driver.get("https://www.notion.so/login")
    time.sleep(10)  # Wait for the login page to load fully

    if not find_and_click_apple_button():
        raise Exception("Failed to find and click 'Continue with Apple' button")

    time.sleep(10)  # Wait for the Apple login page to load

    # Switch to the Apple login iframe
    try:
        driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[contains(@src, 'appleid.apple.com')]"))
        log_message("Switched to Apple login iframe.")
    except Exception as e:
        log_message(f"Failed to switch to Apple login iframe: {e}")
        raise

    # Use environment variables for Apple login details
    try:
        apple_id_input = driver.find_element(By.ID, "account_name_text_field")
        apple_id_input.send_keys(apple_email)
        apple_id_input.send_keys(Keys.RETURN)
        time.sleep(2)

        # Input Apple password
        apple_password_input = driver.find_element(By.ID, "password_text_field")
        apple_password_input.send_keys(apple_password)
        apple_password_input.send_keys(Keys.RETURN)
        log_message("Entered Apple login credentials.")
    except Exception as e:
        log_message(f"Failed to enter Apple login credentials: {e}")
        raise

    time.sleep(10)  # Wait for login to complete

    # Switch back to the main content
    driver.switch_to.default_content()
    log_message("Logged in to Notion with Apple successfully.")


def scrape_first_favorite():
    log_message("Navigating to Notion page for scraping favorites.")
    driver.get(
        "https://www.notion.so/sidex/1x-xxxx-faves-home-favorites-saved-1st-100-cats-2nd-240425-0a27fe7350eb497eb190ed1efeffb74f?pvs=4")

    time.sleep(5)  # Wait for the page to load

    # Take screenshot of the page
    screenshot_path = "notion_screenshot.png"
    driver.save_screenshot(screenshot_path)

    # Extract text from the image
    page_text = extract_text_from_image(screenshot_path)

    # Log the extracted text (for debugging purposes)
    log_message(f"Extracted text: {page_text}")

    # Locate the first favorite by its title
    position = locate_text_position('[ 1x.xxxx ] FAVES Home: Favorites saved 1st. 100 Cats 2nd [240425]',
                                    screenshot_path)

    if position:
        x, y, w, h = position
        log_message(f"Located position of the first favorite: {position}")
        # Simulate clicking the element
        pyautogui.click(x + w / 2, y + h / 2)
        time.sleep(1.5)
        # Attempt to find the copy link option
        more_options_button_position = locate_text_position('More options', screenshot_path)
        if more_options_button_position:
            x, y, w, h = more_options_button_position
            pyautogui.click(x + w / 2, y + h / 2)
            time.sleep(1.5)
            copy_link_button_position = locate_text_position('Copy link', screenshot_path)
            if copy_link_button_position:
                x, y, w, h = copy_link_button_position
                pyautogui.click(x + w / 2, y + h / 2)
                time.sleep(1.5)
                # Extract the link
                link = pyperclip.paste()
                log_message(f"Scraped first favorite link: {link}")
                return [link]
    else:
        log_message("Failed to locate the first favorite.")
        return []


def update_notion(favorites):
    # Fetch the existing page content
    try:
        # Update the Notion page
        children = []
        for favorite in favorites:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": favorite
                            }
                        }
                    ]
                }
            })

        notion.blocks.children.append(block_id=notion_page_id, children=children)
        log_message("Notion page updated successfully.")

        # Update the Notion database
        database_id = 'db3633dd6457459e81cf13ff70d1eeb4'  # Replace with your actual database ID
        for favorite in favorites:
            notion.pages.create(parent={"database_id": database_id}, properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": favorite
                            }
                        }
                    ]
                }
            })
        log_message("Notion database updated successfully.")
    except Exception as e:
        log_message(f"Failed to update Notion page or database: {e}")


# Main function
def main():
    login_to_notion_with_apple()
    favorites = scrape_first_favorite()
    update_notion(favorites)
    driver.quit()


if __name__ == "__main__":
    main()
