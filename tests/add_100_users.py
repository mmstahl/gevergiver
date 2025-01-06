from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import random
import sys

# Function to generate users
def generate_users():
    users = []
    for i in range(1, 101):
        username = f"user{i:03d}"
        password = username
        users.append({"username": username, "password": password})
    return users

# Function to simulate login
def simulate_login(driver, user, url):
    driver.get(url)
    username_input = driver.find_element(By.NAME, "username") 
    password_input = driver.find_element(By.NAME, "password")    
    username_input.send_keys(user["username"])
    password_input.send_keys(user["password"])
    password_input.send_keys(Keys.RETURN)
    time.sleep(random.uniform(1, 3))  # Random delay to simulate real user behavior

def main(login_url):
    # Initialize WebDriver (assuming chromedriver is in PATH)
    driver = webdriver.Chrome()

    # Generate users
    users = generate_users()

    # Simulate logins for all users
    for user in users:
        simulate_login(driver, user, login_url)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <login_url>")
        sys.exit(1)

    login_url = sys.argv[1]
    main(login_url)
