from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# -----------------------------
# Browser Setup (Selenium 4)
# -----------------------------
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

wait = WebDriverWait(driver, 10)

driver.get("https://the-internet.herokuapp.com/")
time.sleep(2)

# =================================================
# 1️⃣ Redirect Link
# =================================================
wait.until(EC.element_to_be_clickable(
    (By.LINK_TEXT, "Redirect Link")
)).click()
time.sleep(2)

wait.until(EC.element_to_be_clickable(
    (By.ID, "redirect")
)).click()

wait.until(EC.url_contains("status_codes"))
time.sleep(2)

# =================================================
# 2️⃣ File Upload
# =================================================
driver.get("https://the-internet.herokuapp.com/upload")
time.sleep(2)

file_path = os.path.abspath("upload_test.txt")
with open(file_path, "w") as f:
    f.write("Selenium file upload test")

wait.until(EC.presence_of_element_located(
    (By.ID, "file-upload")
)).send_keys(file_path)

wait.until(EC.element_to_be_clickable(
    (By.ID, "file-submit")
)).click()
time.sleep(3)

# =================================================
# 3️⃣ Geolocation
# =================================================
driver.get("https://the-internet.herokuapp.com/geolocation")
time.sleep(2)

wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[text()='Where am I?']")
)).click()

time.sleep(5)  # allow map & browser permission popup

# =================================================
# 4️⃣ Entry Ad (Modal)
# =================================================
driver.get("https://the-internet.herokuapp.com/entry_ad")
time.sleep(2)

modal_close = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//div[@class='modal-footer']/p")
))
modal_close.click()
time.sleep(2)

# =================================================
# 5️⃣ Dropdown (NEW)
# =================================================
driver.get("https://the-internet.herokuapp.com/dropdown")
time.sleep(2)

dropdown_element = wait.until(EC.presence_of_element_located(
    (By.ID, "dropdown")
))

dropdown = Select(dropdown_element)
dropdown.select_by_visible_text("Option 2")

time.sleep(3)

# -----------------------------
# Close Browser
# -----------------------------
driver.quit()
