#!/usr/bin/env python3

import os
import sys
import ssl
from sources.browser import create_driver
from sources.browser import Browser
import time

# Bypass SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

def test_api_init():
    print("Testing API initialization with Chrome fix...")
    
    try:
        # Initialize Chrome with our fixed settings
        print("Creating Chrome driver...")
        driver = create_driver(headless=False, stealth_mode=False)
        
        # Create browser instance
        print("Creating Browser instance...")
        browser = Browser(driver, anticaptcha_manual_install=False)
        
        # Test navigation
        print("Testing navigation to Google...")
        driver.get("https://www.google.com")
        time.sleep(3)
        title = driver.title
        print(f"Page title: {title}")
        
        # Take screenshot for verification
        print("Taking screenshot...")
        if not os.path.exists(".screenshots"):
            os.makedirs(".screenshots")
        driver.save_screenshot(".screenshots/api_test.png")
        
        # Clean up
        print("Closing browser...")
        driver.quit()
        
        print("Test completed successfully!")
        return True
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    if test_api_init():
        print("API initialization test passed.")
        sys.exit(0)
    else:
        print("API initialization test failed.")
        sys.exit(1) 