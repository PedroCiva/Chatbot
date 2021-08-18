from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import re

driver = webdriver.Chrome()
def input_login():
    global email
    global password

 #TODO uncomment this
   # print("Please login into your Replika AI account:")
    #email = input("E-mail:")
    #password = input("Password:")

def enter_chat_website():
    driver.get("https://my.replika.ai/")
    driver.find_element_by_css_selector(
        "#root > div > div.FullscreenLayout__FullscreenBody-sc-1a0qg1-11.bVqheJ > main > a.Welcome__LoginLink-sc-15ulcz8-1.faTsSk").click()
    time.sleep(3)

def perform_login():

    # Send our e-mail and click next
    email_field = driver.find_element_by_css_selector("#emailOrPhone")
    email_field.send_keys("pwiltus@hotmail.com")  # TODO replace for email
    driver.find_element_by_css_selector("#loginForm > button").click()

    time.sleep(1) # Wait for website

    # Send our password and click next
    password_field = driver.find_element_by_css_selector("#login-password")
    password_field.send_keys("B@squete123")  # TODO replace for password
    time.sleep(1)
    driver.find_element_by_css_selector("#loginForm > button").click()
    time.sleep(2)
    if driver.current_url != "https://my.replika.ai/":
        print("Error, try again")
        enter_chat_website()
        input_login()
        perform_login()
    else:
        print("Login successfull!")

# Chat methods
def send_message(message):
    # Find message area, input message and send
    text_area = driver.find_element_by_css_selector("#send-message-textarea")
    text_area.send_keys(message)
    text_area.send_keys(Keys.ENTER)


ai_messages = []
last_ai_message = ""  # TODO: In case there are 2 last messages, how to get them both?
def main():
    # Enter Replika AI website
    enter_chat_website()

    # Login
    input_login()
    perform_login()

    # Allow time for the chat to load
    time.sleep(10)

def GetMessage():
    # Get chat
    chat = driver.find_elements_by_css_selector("[id^='message']")
    # TODO: Remove "Renee says:" and the time label from the chat string
    text = ""
    for elem in chat:
        text = elem.get_attribute("aria-label")
        if text is None or "you say:" in text:  # Filtering out our own messages
            continue
        else:
            text = (str((text).partition(", at")[0]))  # Filtering out time stamp
            ai_messages.append(text)
            last_ai_message = ai_messages[len(ai_messages) - 1]
    print(last_ai_message)
    return last_ai_message








# TODO: verify if subscription popup shows up , selector = #dialog-scroll > div > div > button > svg > g > path
#if __name__ == "__main__":
 #   main()