from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import random
import sys
from concurrent.futures import ThreadPoolExecutor

def simulate_login(driver, username, password, url):
    driver.get(url)
    time.sleep(2)  # Allow time for the page to load

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
    points_to_transfer = 11
    # points_to_transfer = random.randint(0, max_points)
    points_input = driver.find_element(By.NAME, "points")
    points_input.send_keys(str(points_to_transfer))

    transfer_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Transfer Points')]")
    transfer_button.click()
    time.sleep(2)  # Allow time for the transfer to process

def user_task(username, password, url):
    driver = webdriver.Chrome()
    for _ in range(10):
        try:
            simulate_login(driver, username, password, url)
            click_view_players(driver)
            select_random_player(driver)

            giver_points_text = driver.find_element(By.XPATH, "//p[contains(text(), 'Your GiverPoints')]").text
            max_points = int(giver_points_text.split(":")[1].strip())
            
            transfer_random_points(driver, max_points)
        except Exception as e:
            print(f"An error occurred for user {username}: {e}")

        # Wait for a random number of seconds between 5 and 10
        wait_time = random.randint(5, 10)
        time.sleep(wait_time)

    driver.quit()

def main(url):
    # Generate users
    users = [f"user{i:03d}" for i in range(1, 101)]
    
    # Select 5 users
    selected_users = random.sample(users, 100)
    
    # Run tasks in parallel for each selected user
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for username in selected_users:
            password = username
            futures.append(executor.submit(user_task, username, password, url))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <login_url>")
        sys.exit(1)

    login_url = sys.argv[1]
    main(login_url)
