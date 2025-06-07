#!/usr/bin/env python3

import os
import sys
import ssl
import time
import subprocess
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Fix macOS SSL certificate issues
ssl._create_default_https_context = ssl._create_unverified_context

def fix_chrome_browser():
    """Fix Chrome browser initialization on macOS"""
    print("macOS Chrome Fix Script")
    print("======================")
    
    # Check for Chrome
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome_path):
        print("❌ Chrome not found! Please install Chrome first.")
        return False
    
    # Check Chrome version
    try:
        chrome_version = subprocess.check_output([chrome_path, "--version"]).decode().strip()
        print(f"✓ Found Chrome: {chrome_version}")
    except:
        print("❌ Failed to check Chrome version")
        return False
    
    # Set up unique Chrome profile
    unique_profile = tempfile.mkdtemp(prefix="chrome_profile_")
    print(f"✓ Created unique Chrome profile at: {unique_profile}")
    
    # Set up minimal Chrome options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={unique_profile}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    print("Attempting to start Chrome...")
    try:
        # Try to create browser without explicit ChromeDriver
        driver = webdriver.Chrome(options=options)
        print("✓ Chrome initialized successfully without explicit ChromeDriver!")
        
        # Test it
        print("Navigating to Google...")
        driver.get("https://www.google.com")
        time.sleep(2)
        title = driver.title
        print(f"✓ Loaded page with title: {title}")
        
        # Take screenshot as proof
        screenshot_path = "fixed_chrome.png"
        driver.save_screenshot(screenshot_path)
        print(f"✓ Screenshot saved to {screenshot_path}")
        
        driver.quit()
        print("✓ Chrome initialized and tested successfully!")
        
        # Create instructions to update browser.py
        with open("chrome_fix_instructions.txt", "w") as f:
            f.write("# Chrome Fix Instructions\n\n")
            f.write("Add these lines to the top of sources/browser.py:\n\n")
            f.write("```python\n")
            f.write("# Fix macOS SSL certificate issues\n")
            f.write("import ssl\n")
            f.write("ssl._create_default_https_context = ssl._create_unverified_context\n")
            f.write("```\n\n")
            f.write("Replace create_driver function with:\n\n")
            f.write("```python\n")
            f.write("def create_driver(headless=False, stealth_mode=True, crx_path='./crx/nopecha.crx', lang='en'):\n")
            f.write("    # Create options with minimal settings for macOS\n")
            f.write("    options = Options()\n")
            f.write("    options.add_argument('--no-sandbox')\n")
            f.write("    options.add_argument('--disable-dev-shm-usage')\n")
            f.write("    options.add_argument('--disable-gpu')\n")
            f.write("    options.add_argument(f'--user-data-dir={tempfile.mkdtemp(prefix=\"chrome_profile_\")}')\n")
            f.write("    options.add_argument('--disable-blink-features=AutomationControlled')\n")
            f.write("    options.add_experimental_option('excludeSwitches', ['enable-automation'])\n")
            f.write("    options.add_experimental_option('useAutomationExtension', False)\n")
            f.write("\n")
            f.write("    # Try to create browser without explicit ChromeDriver\n")
            f.write("    return webdriver.Chrome(options=options)\n")
            f.write("```\n")
        
        print("✓ Created instructions for fixing browser.py in chrome_fix_instructions.txt")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Chrome: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_chrome_browser()
    
    if success:
        print("\n✅ Chrome fix completed successfully!")
        print("Please check chrome_fix_instructions.txt for update instructions.")
        sys.exit(0)
    else:
        print("\n❌ Chrome fix failed.")
        print("Please try the following:")
        print("1. Close all Chrome instances completely")
        print("2. Check macOS security permissions for Chrome")
        print("3. Make sure Chrome is up to date")
        sys.exit(1) 