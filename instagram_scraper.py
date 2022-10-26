import argparse
import os
import selenium.webdriver as webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import wget

insta_page = 'https://www.instagram.com/'

import re

# https://www.selenium.dev/selenium/docs/api/py/ In case you have special characters in your password, please add "\"
# before them in the password and the script will work as expected

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Instagram profile scrapper configurations', add_help=False)
    parser.add_argument('--insta-username', type=str,
                        help='Instagram your profile username', required=True)
    parser.add_argument('--insta-password', type=str, help='Instagram your profile password', required=True)

    parser.add_argument('--insta-profile-id', type=str, help='Instagram profile username to scrap', required=True)
    parser.add_argument('--op-folder', type=str, default='insta_profiles', help='Output folder path')
    parser.add_argument('--seconds-to-wait', type=int, default=5, help='Number of seconds to wait between each '
                                                                        'request of the data (scrolling for instance)')
    parser.add_argument('--public-page', action='store_true', help='To know if it is a public page')
    args = parser.parse_args()

    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'
    FireFoxDriverPath = os.path.join(os.getcwd(), 'Drivers', 'geckodriver')
    firefox_service = Service(FireFoxDriverPath)
    firefox_option = Options()
    firefox_option.set_preference("general.useragent.override", user_agent)
    browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
    wait = WebDriverWait(browser, 50)

    if not args.public_page:
        browser.get(insta_page)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_a9-- _a9_0']"))).click()
        time.sleep(1)
        # Login with credentials
        wait.until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(args.insta_username)
        wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(args.insta_password)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _abak _abb8 _abbq _abb- _abcm']"))).click()
        print("Logged in")

        time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_acan _acap _acas']"))).click()
        print("Save info is clicked")

        # Turn off notifications
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_a9-- _a9_1']"))).click()
        print("Turn off notification is clicked")
        time.sleep(2)

    insta_page = insta_page + args.insta_profile_id
    browser.get(insta_page)
    print(f"The username {args.insta_profile_id} has been loaded")

    print('Scrolling down')
    # Get the screen height
    screen_height = browser.execute_script("return window.screen.height;")
    new_scroll_height = screen_height

    # Get the screen height
    scroll_height = 0
    # Use while loop to keep scrolling non-stop
    i = 1
    # Record the starting time of the loop
    start = time.time()
    images_dict = {}
    while True:
        # Scroll 1 screen height each time
        while True:
            new_scroll_height = int(new_scroll_height) + 10
            browser.execute_script(f"window.scrollTo(0, {new_scroll_height});")
            if new_scroll_height > screen_height * i:
                break
        i += 1
        # Allow for pause time to load data
        print(f'Waiting {args.seconds_to_wait} seconds')
        time.sleep(args.seconds_to_wait)
        new_scroll_height = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9o _abcm']"))).get_attribute('scrollHeight')

        # Record ending time of the whole loop
        end = time.time()
        # todo : I modified this presence_of_all_elements_located to visibility_of_element_located
        a = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//img[@class='x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3']")))
        print(len(a))

        for ind, element in enumerate(a):
            key = f"{element.get_attribute('src').split('&')[-2]}_{element.get_attribute('alt')}"
            print(key)
            if key not in images_dict:
                # print(element.get_attribute('src'))
                images_dict[key] = element.get_attribute('src')

        # Break the loop with a given time limit
        if new_scroll_height == scroll_height:
            break
        scroll_height = new_scroll_height
    print('Finish Scrolling..')
    print(f"Number of images extracted are {len(images_dict)}")

    if not os.path.exists(args.op_folder):
        os.mkdir(args.op_folder)
    output_folder = os.path.join(args.op_folder, args.insta_profile_id)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # download images
    for key in images_dict:
        print(f'\nDownloading {key}')
        image_name = key
        if len(image_name) > 150:
            image_name = image_name[0: 150]
            print(image_name)
        save_as = os.path.join(output_folder, image_name.replace("/"," ") + '.jpg')
        wget.download(images_dict[key], save_as)
