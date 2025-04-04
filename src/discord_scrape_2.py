import time
import csv
import re
import random
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# === CONFIGURATION ===
DISCORD_CHANNELS_OUTPUT = "discord_channels.csv"
DISCORD_MEMBERS_OUTPUT = "discord_scraped_members.csv"
DELAY_BETWEEN_ACTIONS = 5
MAX_MEMBERS_PER_SERVER = 20

# === SETUP SELENIUM ===
service = Service(executable_path="chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Keeps your logged-in session
options = uc.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
options.add_argument("--start-maximized")
options.add_argument(r"--user-data-dir=C:\\Users\\okoro\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument('--profile-directory=Default')

driver = uc.Chrome(options=options)
# === FUNCTIONS ===

def human_delay(min_sec=2.5, max_sec=5.5):
    """Sleep for a random time between min_sec and max_sec to mimic human behavior."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

# === FUNCTIONS ===
def get_channel_links():
    """Get all valid server links from the sidebar using class selectors."""
    print(" Collecting Discord server links...")
    channels = []

    try:
        human_delay()
        channel_elements = driver.find_elements(By.CLASS_NAME, "wrapper__6e9f8")

        if not channel_elements:
            print(" No elements found with class 'wrapper__6e9f8'. Check if Discord UI has changed.")
            return []
        else:
            print(f" Found {len(channel_elements)} elements with class 'wrapper__6e9f8'. Processing...")

        for channel in channel_elements:
            try:
                data_list_item_id = channel.get_attribute("data-list-item-id")
                print(f" Found element with data-list-item-id: {data_list_item_id}")

                if data_list_item_id and "guildsnav___" in data_list_item_id:
                    # Extract only the numeric server ID after "guildsnav___"
                    channel_id_match = re.search(r'guildsnav___(\d+)', data_list_item_id)
                    
                    if channel_id_match:
                        channel_id = channel_id_match.group(1)
                        channel_link = f"https://discord.com/channels/{channel_id}"

                        if channel_link not in channels:
                            channels.append(channel_link)
                            print(f" Extracted and saved channel link: {channel_link}")
                    else:
                        print(f" Failed to extract numeric ID from: {data_list_item_id}")
            except Exception as e:
                print(f" Error processing a channel element: {e}")

    except Exception as e:
        print(f" Error collecting channels: {e}")

    print(f" Total channels found: {len(channels)}")
    return channels

def save_channels_to_csv(channel_list):
    """Save found channels to a CSV file."""
    with open(DISCORD_CHANNELS_OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for channel in channel_list:
            writer.writerow([channel])
    print(f" Saved {len(channel_list)} channels to {DISCORD_CHANNELS_OUTPUT}")

def get_server_name():
    """Extracts the server name."""
    try:
        server_name_elem = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[1]/div[1]/nav/div[1]/header/div/h2')
        return server_name_elem.text.strip()
    except Exception as e:
        print(f" Could not retrieve server name: {e}")
        return "Unknown Server"

def scrape_members_list():
    """Scrape members from the dedicated Members List page."""
    print(" Checking for Members List button...")
    try:
        member_list_button = driver.find_element(By.XPATH, '//*[@id="channels"]/ul/div[3]/li/div/div[2]')
        if member_list_button:
            print(" Members List button found! Clicking...")
            member_list_button.click()
            human_delay()

            # Locate the members table
            tbody = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[1]/div/div/table/tbody')
            members = tbody.find_elements(By.TAG_NAME, 'tr')

            print(f" Found {len(members)} members in the list.")

            extracted_members = []
            for index, member in enumerate(members[:MAX_MEMBERS_PER_SERVER]):  # Limit to max members
                try:
                    # Locate the username inside the row
                    username_elem = member.find_element(By.XPATH, f'./td[1]/div/div[3]/span/span')
                    username = username_elem.text.strip()
                    if username:
                        print(f" {index+1}. {username}")
                        extracted_members.append((username, "N/A"))
                except Exception as e:
                    print(f" Error extracting username for member {index+1}: {e}")

            return extracted_members
    except Exception:
        print(" No dedicated Members List button found. Trying Members Panel...")
        return []

def scrape_members_panel():
    """Scrape members from the Members Panel when the Members List button isn't available."""
    print(" Checking for Members Panel...")
    try:
        members_panel = driver.find_element(By.CSS_SELECTOR, 'div[role="list"][aria-label="Members"].content__99f8c')

        members = members_panel.find_elements(By.XPATH, '//*[contains(@class, "clickable__91a9d")]')

        print(f" Found {len(members)} members in the panel.")

        extracted_members = []
        for index, member in enumerate(members[:MAX_MEMBERS_PER_SERVER]):
            try:
                ActionChains(driver).move_to_element(member).perform()
                time.sleep(2)
                member.click()
                time.sleep(2)

                # Small modal appears, now locate Options button
                options_button = driver.find_element(By.XPATH, '//button[contains(@class, "button_fb7f94")]')
                options_button.click()
                time.sleep(2)

                # Click "View Full Profile"
                view_profile_option = driver.find_element(By.XPATH, '//*[@id="user-profile-overflow-menu-view-profile"]')
                view_profile_option.click()
                time.sleep(2)

                # Extract details from the full profile modal
                username_elem = driver.find_element(By.XPATH, '//*[@id="app-mount"]/div[2]/div[1]/div[4]/div[2]/div/div/div/div/div[2]/div[1]/div[2]/div[1]/span[1]')
                username = username_elem.text.strip()

                joined_elem = driver.find_element(By.XPATH, '//*[@id="app-mount"]/div[2]/div[1]/div[4]/div[2]/div/div/div/div/div[2]/div[2]/div/div[2]/section[2]/div[2]/div[3]/div[2]')
                joined_date = format_date(joined_elem.text.strip())

                print(f" {index+1}. {username} - {joined_date}")
                extracted_members.append((username, joined_date))

                # Click backdrop to close modal
                backdrop = driver.find_element(By.XPATH, '//*[@id="app-mount"]/div[2]/div[1]/div[4]/div[1]')
                backdrop.click()
                time.sleep(2)

            except Exception as e:
                print(f" Error extracting member {index+1}: {e}")

        return extracted_members
    except Exception as e:
        print(f" Members Panel not found: {e}")
        return []

def format_date(raw_date):
    """Convert raw Discord date to a user-friendly format."""
    match = re.search(r"(\d{1,2}) (\w+) (\d{4})", raw_date)
    if match:
        day = int(match.group(1))
        month = match.group(2)
        year = match.group(3)

        suffix = "th"
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        return f"Joined on {day}{suffix} of {month} {year}"
    return raw_date

def save_members_to_csv(server_name, server_url, member_list):
    """Save found members to a CSV file."""
    with open(DISCORD_MEMBERS_OUTPUT, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for member, date_joined in member_list:
            writer.writerow([server_name, server_url, member, date_joined])
    print(f" Saved {len(member_list)} members to {DISCORD_MEMBERS_OUTPUT}")

# === MAIN PROCESS ===
try:
    driver.get("https://discord.com/channels/@me")
    time.sleep(DELAY_BETWEEN_ACTIONS * 2)

    servers = get_channel_links() # Replace with real server IDs

    for server_url in servers:
        print(f"\n Processing server: {server_url}")
        driver.get(server_url)
        human_delay()

        server_name = get_server_name()
        members = scrape_members_list()

        if not members:
            members = scrape_members_panel()

        if members:
            save_members_to_csv(server_name, server_url, members)
        else:
            print(f" No new members found in {server_url}")

    print("\n Discord scraping complete!")

except Exception as e:
    print(f" Critical error: {e}")

finally:
    driver.quit()
    print(" Browser closed.")
