import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# === CONFIGURATION ===
SEARCH_QUERY = "learn trading"
MAX_PROFILES = 500
MAX_FOLLOWINGS_TO_CHECK = 20
DELAY_BETWEEN_ACTIONS = 3
DISCORD_CSV = "twitter_discord_links.csv"
WEBSITES_CSV = "twitter_websites.csv"
TELEGRAM_CSV = "twitter_telegram_links.csv"

# === SETUP SELENIUM ===
service = Service(executable_path="chromedriver.exe")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

# Optional: use your logged-in profile
options.add_argument(r"--user-data-dir=C:\\Users\\okoro\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument(r"--profile-directory=Default")

# Uncomment for headless operation after testing
options.add_argument("--headless=new")

driver = webdriver.Chrome(service=service, options=options)

# === SAVE FUNCTIONS ===
def save_to_csv(filename, data_row):
    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data_row)

# === SCRAPE FUNCTIONS ===
def search_twitter(query):
    print(f" Searching X.com for: {query}")
    search_url = f"https://x.com/search?q={query}&src=typed_query&f=user"
    driver.get(search_url)
    time.sleep(DELAY_BETWEEN_ACTIONS)

def scroll_and_collect_profiles(max_profiles):
    print(f" Scrolling to collect profiles (limit: {max_profiles})")
    profiles = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(profiles) < max_profiles:
        # Narrow down to profile links by ensuring hrefs start with https://x.com/username (exclude home, explore, etc.)
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "https://x.com/") and not(contains(@href, "/status/")) and not(contains(@href, "/explore")) and not(contains(@href, "/notifications")) and not(contains(@href, "/messages")) and not(contains(@href, "/compose")) and not(contains(@href, "/home")) and not(contains(@href, "/i/")) and not(contains(@href, "communities")) and @role="link"]')

        for link in links:
            profile_url = link.get_attribute("href")
            if profile_url and profile_url not in profiles:
                profiles.add(profile_url)
                print(f" Found profile: {profile_url}")
                if len(profiles) >= max_profiles:
                    break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(DELAY_BETWEEN_ACTIONS)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print(" No more profiles found while scrolling.")
            break
        last_height = new_height

    print(f" Collected {len(profiles)} profiles.")
    return list(profiles)

def scrape_profile(profile_url):
    print(f" Checking profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(DELAY_BETWEEN_ACTIONS)

    bio_text = ""
    website_link = ""
    discord_link = ""
    telegram_link = ""

    try:
        # Bio Text
        bio_element = driver.find_element(By.XPATH, '//div[contains(@data-testid, "UserDescription")]')
        bio_text = bio_element.text.lower()
        print(f" Bio: {bio_text}")

        # Links Section (website and others)
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "http") and not(contains(@role, "link"))]')
        for link in links:
            href = link.get_attribute("href")
            if "discord" in href and not discord_link:
                discord_link = href
            elif "t.me" in href or "telegram" in href:
                telegram_link = href
            elif not website_link:
                website_link = href

        if discord_link:
            username = profile_url.split("/")[-1]
            save_to_csv(DISCORD_CSV, [username, discord_link])
            print(f" Discord link found and saved: {discord_link}")

            if website_link:
                save_to_csv(WEBSITES_CSV, [username, website_link])
                print(f" Website link saved: {website_link}")

            if telegram_link:
                save_to_csv(TELEGRAM_CSV, [username, telegram_link])
                print(f" Telegram link saved: {telegram_link}")

            # Proceed to check followings if Discord link found
            check_followings(profile_url, username)

    except Exception as e:
        print(f" Error scraping profile bio: {e}")

def check_followings(profile_url, username):
    print(f" Checking followings for {username}")

    followings_url = profile_url + "/following"
    driver.get(followings_url)
    time.sleep(DELAY_BETWEEN_ACTIONS)

    followings = set()
    count = 0

    while len(followings) < MAX_FOLLOWINGS_TO_CHECK:
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "https://x.com/") and not(contains(@href, "/status/")) and not(contains(@href, "/explore")) and not(contains(@href, "/notifications")) and not(contains(@href, "/messages")) and not(contains(@href, "/compose")) and not(contains(@href, "/home")) and not(contains(@href, "/i/")) and not(contains(@href, "communities")) and @role="link"]')

        for link in links:
            following_url = link.get_attribute("href")
            if following_url and following_url not in followings:
                followings.add(following_url)
                print(f" Found following profile: {following_url}")
                scrape_profile(following_url)
                count += 1
                if count >= MAX_FOLLOWINGS_TO_CHECK:
                    break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(DELAY_BETWEEN_ACTIONS)

        if count >= MAX_FOLLOWINGS_TO_CHECK:
            break

# === MAIN PROCESS ===
try:
    search_twitter(SEARCH_QUERY)
    profile_urls = scroll_and_collect_profiles(MAX_PROFILES)

    print(f"\n Visiting profiles to find Discord links...\n")
    for idx, profile_url in enumerate(profile_urls):
        print(f" {idx + 1}/{len(profile_urls)}: {profile_url}")
        scrape_profile(profile_url)
        time.sleep(DELAY_BETWEEN_ACTIONS)

    print("\n Scraping complete!")

except Exception as e:
    print(f" An error occurred: {e}")

finally:
    driver.quit()
