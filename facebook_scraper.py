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
import pandas as pd

import re
fb_page = 'https://www.facebook.com/'

# https://www.selenium.dev/selenium/docs/api/py/ In case you have special characters in your password, please add "\"
# before them in the password and the script will work as expected

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Facebook profile scrapper configurations', add_help=False)
    parser.add_argument('--fb-username', type=str,
                        help='Facebook your profile username', required=True)
    parser.add_argument('--fb-password', type=str, help='Facebook your profile password', required=True)

    parser.add_argument('--fb-profile-id', type=str, help='Facebook profile username to scrap', required=True)
    parser.add_argument('--op-folder', type=str, default='profiles', help='Output folder path')
    parser.add_argument('--seconds-to-wait', type=int, default=5, help='Number of seconds to wait between each '
                                                                        'request of the data (scrolling for instance)')
    args = parser.parse_args()

    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'
    FireFoxDriverPath = os.path.join(os.getcwd(), 'Drivers', 'geckodriver')
    firefox_service = Service(FireFoxDriverPath)
    firefox_option = Options()
    firefox_option.set_preference("general.useragent.override", user_agent)
    browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
    wait = WebDriverWait(browser, 20)

    browser.get(fb_page)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_42ft _4jy0 _9xo7 _4jy3 _4jy1 selected _51sy']"))).click()
    time.sleep(1)
    # Login with credentials
    wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(args.fb_username)
    wait.until(EC.element_to_be_clickable((By.NAME, "pass"))).send_keys(args.fb_password)
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@class='_6ltg']"))).click()
    print("Logged in")

    # time.sleep(2)
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_acan _acap _acas']"))).click()
    # print("Save info is clicked")
    #
    # # Turn off notifications
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_a9-- _a9_1']"))).click()
    # print("Turn off notification is clicked")
    time.sleep(2)

    if not os.path.exists(args.op_folder):
        os.mkdir(args.op_folder)
    output_folder = os.path.join(args.op_folder, args.fb_profile_id)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    fb_2_pages_photos = ['photos_of', 'photos_by']
    for fb_uri in fb_2_pages_photos:

        fb_page_photos = fb_page + args.fb_profile_id + '/' + fb_uri
        browser.get(fb_page_photos)
        print(f"\nThe page {fb_page_photos} has been loaded")

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
        images_list = []

        while True:
            # Scroll 1 screen height each time
            while True:
                new_scroll_height = int(new_scroll_height) + 10
                browser.execute_script(f"window.scrollTo(0, {new_scroll_height});")
                if new_scroll_height > screen_height * i:
                    break
            i += 1
            print(f'Waiting {args.seconds_to_wait} seconds')
            time.sleep(args.seconds_to_wait)
            new_scroll_height = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='x9f619 x1n2onr6 x1ja2u2z xeuugli x1iyjqo2 xs83m0k x1xmf6yo x1emribx x1e56ztr "
                           "x1i64zmx xjl7jj x1l7klhg x193iq5w']"))).get_attribute('scrollHeight')

            end = time.time()
            a = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH,
                 "//a[@class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xe8uvvx xdj266r x11i5rnm "
                 "xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv "
                 "x1lliihq x5yr21d x1n2onr6 xh8yej3']")))
            print(len(a))

            for ind, element in enumerate(a):
                key = element.get_attribute('href')
                if key not in images_list:
                    # print(element.get_attribute('src'))
                    images_list.append(key)

            # Break the loop with a given time limit
            if new_scroll_height == scroll_height:
                break
            scroll_height = new_scroll_height
        print('Finish Scrolling..')
        print(f"Number of links for images are {len(images_list)}")

        # time.sleep(2)
        images_dict = {}
        post_description = []
        for image_link in images_list:
            print(image_link)
            browser.get(image_link)
            try:
                img = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//img[@class='x85a59c x193iq5w x4fas0m x19kjcj4']")))

                div_span_posts = []
                try:
                    div_span_posts = wait.until(EC.presence_of_all_elements_located(
                        (By.XPATH, "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x "
                                   "x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u']")))
                except Exception as ex:
                    print(f"This link {image_link} does not have any comments or any description")

                if len(div_span_posts) > 0:
                    text_content = div_span_posts[0].get_attribute('textContent')
                    print(text_content)

                for element in img:
                    key = f"{fb_uri}_{element.get_attribute('src').split('&')[-2]}_{element.get_attribute('alt')}"
                    if key not in images_dict:
                        # print(element.get_attribute('src'))
                        images_dict[key] = element.get_attribute('src')
                        post_description.append([key, images_dict[key], text_content if text_content is not None else ""])
            except Exception as ex:
                print(f"This link {image_link} does not have the image we are expecting")

        df = pd.DataFrame(post_description, columns={'img_key', 'img_link', 'post_text'})
        df.to_csv(f"{output_folder}/info_{fb_uri}.csv", index=False)

        # download images
        for key in images_dict:
            print(f'\nDownloading {key}')
            image_name = key
            if len(image_name) > 150:
                image_name = image_name[0: 150]
            save_as = os.path.join(output_folder, image_name.replace("/"," ") + '.jpg')

            wget.download(images_dict[key], save_as)
