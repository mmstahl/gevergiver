from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import random
import sys

def simulate_login(driver, username, password, url):
    driver.get(url)
    time.sleep(1)  # Allow time for the page to load

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(2)  # Allow time for the login process

def click_view_players(driver):
    view_players_button = driver.find_element(By.XPATH, "//button[contains(text(), 'View Players')]")
    view_players_button.click()
    time.sleep(2)  # Allow time for the players page to load

def select_random_player(driver):
    player_buttons = driver.find_elements(By.XPATH, "//button")
    random_button = random.choice(player_buttons)
    random_button.click()
    time.sleep(2)  # Allow time for the transfer page to load

def transfer_random_points(driver, max_points):
    points_to_transfer = random.randint(0, max_points)
    points_input = driver.find_element(By.NAME, "points")
    points_input.send_keys(str(points_to_transfer))

    transfer_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Transfer Points')]")
    transfer_button.click()
    time.sleep(2)  # Allow time for the transfer to process

def main(username, password):
    url = "http://127.0.0.1:5000"

    driver = webdriver.Chrome()
    webdriver.Chrome()

    simulate_login(driver, username, password, url)

    for _ in range(20):
        try:
            click_view_players(driver)
            select_random_player(driver)

            giver_points_text = driver.find_element(By.XPATH, "//p[contains(text(), 'Your GiverPoints')]").text
            max_points = int(giver_points_text.split(":")[1].strip())
            
            transfer_random_points(driver, max_points)
        except Exception as e:
            print(f"An error occurred: {e}")

        # Wait for a random number of seconds between 5 and 10
        wait_time = random.randint(5, 10)
        time.sleep(wait_time)    
    
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    main(username, password)
