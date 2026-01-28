import os
import sys
import time
import requests
import django
from django.core.files.base import ContentFile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 1. Setup Django Environment
# We need this to talk to the Database and RAG Engine
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from evidence_engine.models import SourceDocument
from evidence_engine.ingestion import ingest_document

# --- CONFIGURATION ---
TARGET_URL = "https://www.bnm.gov.my/banking-islamic-banking"
TEMP_DOWNLOAD_DIR = os.path.join(backend_dir, "temp_downloads")

def setup_driver():
    """Starts the Chrome Browser for the Demo with Download Config"""
    print("🚀 Launching Browser for Demo...")
    
    # Ensure temp dir exists and is clean
    if not os.path.exists(TEMP_DOWNLOAD_DIR):
        os.makedirs(TEMP_DOWNLOAD_DIR)
        
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    # 🔧 KEY FIX: Force Chrome to download PDFs instead of opening them
    prefs = {
        "download.default_directory": TEMP_DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True, # It won't view PDF, it will download
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"❌ Browser Driver Error: {e}")
        return None

def download_with_selenium(url, driver):
    """Triggers download via Selenium and returns file content"""
    try:
        # Open in new tab to preserve main page
        driver.execute_script("window.open(arguments[0], '_blank');", url)
        
        # Switch to new tab (to close it specifically if it stays open)
        # Note: If download triggers immediately, the tab might close itself or stay as about:blank
        time.sleep(1.5) 
        
        # Monitor temp folder for new file
        # Timeout 15 seconds
        downloaded_file = None
        for _ in range(30):
            files = [f for f in os.listdir(TEMP_DOWNLOAD_DIR) if not f.endswith('.crdownload')]
            if files:
                # Get the most recent file
                files.sort(key=lambda x: os.path.getmtime(os.path.join(TEMP_DOWNLOAD_DIR, x)))
                downloaded_file = os.path.join(TEMP_DOWNLOAD_DIR, files[-1])
                break
            time.sleep(0.5)
            
        # Close the extra tab if multiple exist
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        if downloaded_file:
            print(f"   ✅ Downloaded: {os.path.basename(downloaded_file)}")
            # Read bytes
            with open(downloaded_file, "rb") as f:
                content = f.read()
            
            # Delete file to clean up for next download
            os.remove(downloaded_file)
            return content
        else:
            print("   ⚠️ Timed out waiting for file.")
            return None
            
    except Exception as e:
        print(f"   ❌ Selenium Download Error: {e}")
        # Ensure we are back on main tab
        if len(driver.window_handles) > 1:
             driver.switch_to.window(driver.window_handles[0])
        return None

def clean_title(raw_text):
    """Sanitizes the document title by removing extra spaces and special characters."""
    if not raw_text:
        return "Untitled_Document"
    # Remove newlines and tabs
    text = raw_text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    # Collapse multiple spaces
    text = ' '.join(text.split())
    # Remove junk suffixes if present
    text = text.replace("Download", "").replace("PDF", "").strip()
    return text

def process_page(driver):
    """Scrapes PDFs from the current visible page"""
    
    links = driver.find_elements(By.TAG_NAME, "a")
    count_on_page = 0
    print(f"\nScanning page for documents...")
    
    pdf_links = []
    for link in links:
        try:
            href = link.get_attribute("href")
            raw_text = link.text
            if href and (".pdf" in href or "/documents/" in href):
                # Apply Cleaning
                text = clean_title(raw_text)
                
                # Check basename if text is still too short (e.g. "Click here")
                if len(text) < 5: 
                    text = clean_title(os.path.basename(href).replace("%20", " "))
                    
                pdf_links.append((href, text))
        except:
            continue
            
    # Process them
    for href, title in pdf_links:
        # 1. Check Duplicates
        if SourceDocument.objects.filter(source_url=href).exists():
            print(f"   ⏭️  Skipping existing: {title[:40]}...")
            continue
            
        print(f"\n🔎 FOUND: {title}")
        print(f"   🔗 URL: {href}")
        
        # 2. Download via Selenium
        print(f"   ⬇️  Downloading...", end="", flush=True)
        content = download_with_selenium(href, driver)
        
        if content:
            # 3. Create Record
            try:
                doc = SourceDocument(
                    title=title,
                    authority=SourceDocument.Authority.BNM,
                    source_url=href,
                    is_ingested=False 
                )
                
                # Clean filename for filesystem
                # User Request: Use {title} as name, but formatted cleanly (no spaces)
                safe_title = title.replace(" ", "_")
                safe_filename = "".join(x for x in safe_title if x.isalnum() or x in "_-")
                filename = f"{safe_filename[:150]}.pdf"
                
                doc.file_path.save(filename, ContentFile(content), save=True)
                if not filename.lower().endswith('.pdf'):
                    filename += ".pdf"
                    
                doc.file_path.save(filename, ContentFile(content), save=True)
                print(f"   💾 Saved to Database (ID: {doc.id})")
                
                print(f"   🧠 Ingesting into AI...", end="", flush=True)
                ingest_document(doc)
                print(" ✅ INGESTED!")
                count_on_page += 1
                
            except Exception as e:
                print(f"\n   ❌ Error saving/ingesting: {e}")
        else:
            print(" ❌ Failed.")

    return count_on_page

def main():
    driver = setup_driver()
    if not driver:
        return
    
    try:
        print(f"🌐 Navigating to {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(5) 
        
        total_ingested = 0
        page = 1
        
        while True:
            print(f"\n--- 📄 PAGE {page} ---")
            
            total_ingested += process_page(driver)
            
            try:
                print("   👀 Looking for 'Next' button...")
                next_btns = driver.find_elements(By.LINK_TEXT, "Next")
                if not next_btns:
                    next_btns = driver.find_elements(By.PARTIAL_LINK_TEXT, "Next")
                
                if next_btns:
                    btn = next_btns[0]
                    if "disabled" in btn.get_attribute("class"):
                        print("   🚫 'Next' is disabled. End of list.")
                        break
                        
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    btn.click()
                    print("   ➡️  Moving to next page...")
                    time.sleep(5)
                    page += 1
                else:
                    print("   🛑 No 'Next' button found.")
                    break
            except Exception as e:
                print(f"   ⚠️ Pagination Error: {e}")
                break
                
        print(f"\n✨ DEMO COMPLETE! Ingested {total_ingested} new documents.")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by User.")
    finally:
        # Cleanup temp dir? Maybe keep for debug. 
        # But we remove individual files as we go.
        driver.quit()

if __name__ == "__main__":
    main()
