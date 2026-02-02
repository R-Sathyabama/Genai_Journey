from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

##Navigation

driver = webdriver.Chrome()
driver.get("https://the-internet.herokuapp.com/")
#driver option

'''
driver.bach()
driver.refresh()
driver.forward()
'''

##Finding elements

#element = driver.find_elements(By.ID,"content")
element = driver.find_elements(By.XPATH, '//*[@id="content"]/ul/li[18]/a')

##Wait

wait = WebDriverWait(driver,10) #process mudiravara wait panum
element = wait.until(EC.presence_of_element_located((By.ID,"content")))  #element therira vara wait panum

##Interaction
"""
element.click()
element.clear()
element.send_key("sathya")
"""

##Screeshot
driver.save_screenshot("ss.png")