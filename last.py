from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.common import exceptions
import csv


def create_webdriver_instance():
    PATH = "C:\Program Files (x86)\chromedriver.exe"

    driver = webdriver.Chrome(executable_path =PATH)
    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return driver

def to_login(driver, id, password2):


    url = "https://twitter.com/i/flow/login/"
    driver.get(url)

    sleep(20)
    login=driver.find_element(By.XPATH,'//input[@name="text"]')
    login.send_keys(id)

    next_btn=driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span')
    next_btn.click()

    sleep(2)
    password=driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password.send_keys(password2)
    login_btn=driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div/span/span')
    login_btn.click()
    sleep(20)
    return True

def twitter_search(driver, name):
    driver.maximize_window()
    sleep(5)

    try:
        search_input=driver.find_element(By.XPATH,'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input')
        search_input.click()
        search_input.send_keys(name)
        search_input.send_keys(Keys.ENTER)
    except AttributeError:
        print("Please Wait")
        try:
            sleep(10)
            search_input=driver.find_element(By.XPATH,'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input')
            search_input.click()
            search_input.send_keys(name)
            search_input.send_keys(Keys.ENTER)
        except:
            print("Check your Internet Connection and try again")
    return True

def change_page_sort(tab_name, driver, nameOfProfile):

    sleep(20)
    profile=driver.find_element(By.LINK_TEXT,nameOfProfile)
    profile.click()
    xpath_tab_state = f'//a[contains(text(),\"{tab_name}\") and @aria-selected=\"true\"]'
    return xpath_tab_state

def collect_all_tweets_from_current_view(driver):

    page_cards = driver.find_elements_by_xpath('//article[@data-testid="tweet"]')
    return page_cards

def extract_data_from_current_tweet_card(card): 

    try:
        user = card.find_element(By.XPATH,'.//span').text
    except exceptions.NoSuchElementException:
        user = ""
    except exceptions.StaleElementReferenceException:
        return
    try:
        postdate = card.find_element(By.XPATH, './/time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        return
    try:
        _comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        _comment = ""
    try:
        _responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        _responding = ""
    tweet_text = _comment + _responding

    tweet = (user, postdate, _responding)
    return tweet

def generate_tweet_id(tweet):
    return ''.join(tweet)

def save_tweet_data_to_csv(records, filepath, mode='a+'):

    header = ['User', 'PostDate', 'TweetText', 'other1', 'other2']
    with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)
        if records:
            writer.writerow(records)

def scroll_down_page(driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
    # """The function will try to scroll down the page and will check the current
    # and last positions as an indicator. If the current and last positions are the same after `max_attempts`
    # the assumption is that the end of the scroll region has been reached and the `end_of_scroll_region`
    # flag will be returned as `True`"""
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region
        
def main(search_term, filepath, username, passs, page_sort='People'):
    save_tweet_data_to_csv(None, filepath, 'w')  # create file for saving records
    unique_tweets = set()
    end_of_scroll_region = False
    last_position = None


    driver = create_webdriver_instance()
    login=to_login(driver, username, passs)
    twitter_search_page_term = twitter_search(driver, search_term)
    if not twitter_search_page_term:
        return

    change_page_sort(page_sort, driver, nameOfProfile='Naughtius Maximus')

    while not end_of_scroll_region:
        postings = collect_all_tweets_from_current_view(driver)#return pagecards with all the tweets header
        for post in postings:
            try:
                tweet = extract_data_from_current_tweet_card(post)
            except exceptions.StaleElementReferenceException:
                continue
            if not tweet:
                continue
            tweet_id = generate_tweet_id(tweet)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet_id)
                save_tweet_data_to_csv(tweet, filepath)
        last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
    driver.quit()
    # if len(unique_tweets)>100:
    #     print(unique_tweets+"\n")
    #     driver.quit()
    #     break

if __name__ == '__main__':
    path = 'elonmusk.csv'
    term = 'Elon Musk'
    username= 'Tafreed18508999'
    passs= 'tmuizahid'
    
    main(term, path, username, passs)