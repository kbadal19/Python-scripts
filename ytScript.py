from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback # Import traceback for better error details

CHANNEL_URL = "https://www.youtube.com/@MannatIVFgynae_centre/videos"

def get_video_links_and_titles():
    options = Options()
    # options.add_argument("--headless=new") # Keep headless commented out for initial debugging if needed
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--log-level=3")
    # Optional: Add a user agent to mimic a real browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print(f"Navigating to {CHANNEL_URL}...")
    driver.get(CHANNEL_URL)

    video_grid_selector = "ytd-rich-grid-renderer #contents"
    # --- CORRECTED SELECTOR ---
    # Selects the anchor tag (<a>) that has the href and title we need.
    video_link_selector = "ytd-rich-grid-media a#video-title-link"

    try:
        print("Waiting for video grid container...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, video_grid_selector))
        )
        print("Video grid container found.")

    except Exception as e:
        print(f"Error waiting for video grid container: {e}")
        print("Traceback:")
        traceback.print_exc() # Print full traceback
        print("Saving page source for debugging...")
        try:
            with open('youtube_page_source_error_grid.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Page source saved to youtube_page_source_error_grid.html")
        except Exception as save_e:
            print(f"Could not save page source: {save_e}")
        driver.quit()
        return []

    print("Scrolling page to load more videos...")
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    scroll_attempts = 0
    max_scroll_attempts = 7 # Adjust as needed, maybe increase if channel has many videos
    no_change_count = 0
    max_no_change = 2 # Stop after N scrolls with no height change

    while scroll_attempts < max_scroll_attempts:
        print(f"Scrolling attempt {scroll_attempts + 1}/{max_scroll_attempts}...")
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(4) # Increased sleep *slightly* might help ensure JS loads
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            no_change_count += 1
            print(f"Scroll height didn't change ({no_change_count}/{max_no_change}).")
            if no_change_count >= max_no_change:
                 print("Reached end of scrollable content (or page stopped loading more).")
                 break
        else:
            no_change_count = 0 # Reset counter if height changed

        last_height = new_height
        scroll_attempts += 1

    if scroll_attempts == max_scroll_attempts:
        print("Reached max scroll attempts.")

    # --- Find elements AFTER scrolling using the CORRECTED selector ---
    print(f"Finding video elements using selector: '{video_link_selector}'...")
    try:
        video_elements = driver.find_elements(By.CSS_SELECTOR, video_link_selector)
        print(f"Found {len(video_elements)} elements.")
    except Exception as find_e:
         print(f"Error finding video elements: {find_e}")
         print("Traceback:")
         traceback.print_exc() # Print full traceback
         print("Saving page source for debugging...")
         try:
             with open('youtube_page_source_find_error.html', 'w', encoding='utf-8') as f:
                 f.write(driver.page_source)
             print("Page source saved to youtube_page_source_find_error.html")
         except Exception as save_e:
             print(f"Could not save page source: {save_e}")
         driver.quit()
         return []


    videos = []
    if video_elements: # Only proceed if elements were found
        print("Processing found elements...")
        for index, video_link_element in enumerate(video_elements):
            try:
                # Basic visibility check (might not be strictly necessary after scrolling)
                # if not video_link_element.is_displayed():
                #      print(f"  Skipping element {index}: Not displayed.")
                #      continue

                url = video_link_element.get_attribute("href")
                title = video_link_element.get_attribute("title") # Primary way to get title

                # --- Optional Fallback: Get text from inner yt-formatted-string if title attribute fails ---
                if not title and url:
                     try:
                         # Find the nested yt-formatted-string by its ID relative to the link
                         inner_title_element = video_link_element.find_element(By.CSS_SELECTOR, "yt-formatted-string#video-title")
                         title = inner_title_element.text
                         print(f"  Used fallback text for element {index}: {title[:50]}...") # Log fallback usage
                     except Exception as title_e:
                         print(f"  Error getting fallback title text for element {index} (URL: {url}): {title_e}")
                         title = "Title Not Found"

                if url and title and title != "Title Not Found":
                    # Basic check to filter out non-video links (e.g., Shorts might appear differently)
                    if "/watch?v=" in url:
                        title_escaped = title.replace("'", "''") # Escape single quotes for SQL
                        videos.append((url, title_escaped))
                        # print(f"  Added: {title_escaped} - {url}") # Uncomment for verbose debugging
                    else:
                        print(f"  Skipping non-video link: {title} - {url}")
                else:
                     # More informative skipping message
                     print(f"  Skipping element {index}: Missing URL ('{url}') or Title ('{title}')")

            except Exception as e:
                # Log the specific error during processing
                print(f"Error processing element at index {index}: {e}")
                # Optionally print traceback for deeper debugging
                # traceback.print_exc()
                continue
    else:
        print("No video elements found after scrolling. Saving page source...")
        try:
             with open('youtube_page_source_no_elements.html', 'w', encoding='utf-8') as f:
                 f.write(driver.page_source)
             print("Page source saved to youtube_page_source_no_elements.html")
        except Exception as save_e:
             print(f"Could not save page source: {save_e}")


    print("Quitting WebDriver...")
    driver.quit()
    print(f"Extracted {len(videos)} valid video links.")
    return videos

# --- generate_sql_insert_statements and main remain the same ---
def generate_sql_insert_statements(videos):
    statements = []
    for url, title in videos:
        description = title # Use the title as the description
        statement = f"INSERT INTO media (type, url, original_name, description) VALUES ('video_url', '{url}', NULL, '{description}');"
        statements.append(statement)
    return statements

def main():
    print("Starting video link scraping...")
    videos = get_video_links_and_titles()
    if not videos:
        print("No videos found or extracted.")
        return

    print(f"\n--- Extracted Videos ({len(videos)}) ---")
    for i, (url, title) in enumerate(videos):
        print(f"{i+1}. {title} - {url}")
    print("--- End of Extracted Videos ---")


    print("\nGenerating SQL statements...")
    sql_statements = generate_sql_insert_statements(videos)
    output_file = 'insert_media.sql'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for stmt in sql_statements:
                f.write(stmt + '\n')
        print(f'\n{len(sql_statements)} SQL insert statements have been written to {output_file}.')
    except Exception as e:
        print(f"Error writing to file {output_file}: {e}")


if __name__ == '__main__':
    main()