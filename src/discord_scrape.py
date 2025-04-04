import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

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
options.add_argument(r"--user-data-dir=C:\\Users\\okoro\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument(r'--profile-directory=Default')

# Initialize driver
driver = webdriver.Chrome(service=service, options=options)


# === FUNCTIONS ===

# === FUNCTIONS ===
def get_channel_links():
    """Get all valid server links from the sidebar using class selectors."""
    print(" Collecting Discord server links...")
    channels = []

    try:
        time.sleep(DELAY_BETWEEN_ACTIONS)
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
    """Scrape members from the main Members List if a dedicated button exists."""
    print(" Checking for Members List button...")
    try:
        member_list_button = driver.find_element(By.XPATH, '//*[@id="channels"]/ul/div[3]/li/div/div[2]')
        if member_list_button:
            print(" Members List button found! Clicking...")
            member_list_button.click()
            time.sleep(DELAY_BETWEEN_ACTIONS)

            # Locate the members table
            tbody = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[1]/div/div/table/tbody')
            members = tbody.find_elements(By.TAG_NAME, 'tr')

            print(f" Found {len(members)} members in the list.")

            member_usernames = []
            for index, member in enumerate(members[:MAX_MEMBERS_PER_SERVER]):  # Limit to max members
                try:
                    # Locate the username inside the row
                    username_elem = member.find_element(By.XPATH, f'./td[1]/div/div[3]/span/span')
                    username = username_elem.text.strip()
                    if username:
                        print(f" {index+1}. {username}")
                        member_usernames.append(username)
                except Exception as e:
                    print(f" Error extracting username for member {index+1}: {e}")

            return member_usernames
    except Exception:
        print(" No dedicated Members List button found. Trying alternative methods...")
        return []

def scrape_welcome_channel():
    """Scrape usernames from the #welcome or #introductions channel."""
    print(" Trying to find #welcome or #introductions channel...")
    try:
        welcome_channel = driver.find_element(By.XPATH, '//nav//div[contains(@aria-label, "welcome") or contains(@aria-label, "introductions")]')
        welcome_channel.click()
        time.sleep(DELAY_BETWEEN_ACTIONS)

        messages = driver.find_elements(By.XPATH, '//h3[contains(@class, "username-")]')
        usernames = [msg.text.strip() for msg in messages[:MAX_MEMBERS_PER_SERVER] if msg.text.strip()]

        print(f" Found {len(usernames)} new members in #welcome.")
        return usernames
    except Exception as e:
        print(f" No welcome channel found: {e}")
        return []

def scrape_booster_list():
    """Scrape usernames from the Server Boosters list."""
    print(" Checking Server Boosters list...")
    try:
        booster_section = driver.find_element(By.XPATH, '//nav//div[contains(@aria-label, "Server Boost")]')
        booster_section.click()
        time.sleep(DELAY_BETWEEN_ACTIONS)

        boosters = driver.find_elements(By.XPATH, '//div[contains(@class, "username-")]')
        usernames = [booster.text.strip() for booster in boosters[:MAX_MEMBERS_PER_SERVER] if booster.text.strip()]

        print(f" Found {len(usernames)} recent boosters.")
        return usernames
    except Exception as e:
        print(f" No Server Boosters list found: {e}")
        return []

def scrape_recently_active_panel():
    """Scrape usernames from the 'Recently Active' user panel."""
    print(" Checking 'Recently Active' user panel...")
    try:
        active_users_section = driver.find_element(By.XPATH, '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[2]/div/section')
        active_users = active_users_section.find_elements(By.XPATH, './/div[contains(@class, "name-")]')

        usernames = [user.text.strip() for user in active_users[:MAX_MEMBERS_PER_SERVER] if user.text.strip()]
        print(f" Found {len(usernames)} recently active users.")
        return usernames
    except Exception as e:
        print(f" No 'Recently Active' panel found: {e}")
        return []

def scrape_reaction_roles():
    """Scrape usernames from reaction roles in public channels."""
    print(" Checking reaction roles in public channels...")
    try:
        reaction_channels = driver.find_elements(By.XPATH, '//nav//div[contains(@aria-label, "roles")]')
        if reaction_channels:
            reaction_channels[0].click()  # Click the first available roles channel
            time.sleep(DELAY_BETWEEN_ACTIONS)

            reactions = driver.find_elements(By.XPATH, '//div[contains(@class, "reaction-")]')
            usernames = [reaction.text.strip() for reaction in reactions[:MAX_MEMBERS_PER_SERVER] if reaction.text.strip()]

            print(f" Found {len(usernames)} reaction role users.")
            return usernames
    except Exception as e:
        print(f" No reaction roles found: {e}")
        return []

def save_members_to_csv(server_name, server_url, member_list):
    """Save found members to a CSV file."""
    with open(DISCORD_MEMBERS_OUTPUT, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for member in member_list:
            writer.writerow([server_name, server_url, member])
    print(f" Saved {len(member_list)} members to {DISCORD_MEMBERS_OUTPUT}")

# === MAIN PROCESS ===
try:
    driver.get("https://discord.com/channels/@me")
    time.sleep(DELAY_BETWEEN_ACTIONS * 2)

    # Step 1: Get server links
    servers = get_channel_links()  # You should load this from your extracted server list CSV

    # Step 2: Scrape members from each server
    for server_url in servers:
        print(f"\n Processing server: {server_url}")
        driver.get(server_url)
        time.sleep(DELAY_BETWEEN_ACTIONS)

        server_name = get_server_name()
        members = scrape_members_list()

        # If the dedicated Members List button was not found, try alternative methods
        if not members:
            members = scrape_welcome_channel()
        if not members:
            members = scrape_reaction_roles()    
        if not members:
            members = scrape_booster_list() 
        if not members:
            members = scrape_recently_active_panel()


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
