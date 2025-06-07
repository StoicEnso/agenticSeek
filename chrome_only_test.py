#!/usr/bin/env python3

import os
import sys
import time
from sources.browser import Browser, create_driver
from sources.utility import pretty_print

def test_chrome_in_api():
    """Test Chrome initialization as it would be used in the API"""
    print("\n==== Chrome Browser Test ====\n")
    
    try:
        print("Initializing Chrome browser...")
        driver = create_driver(headless=False, stealth_mode=False)
        
        # Test basic functionality
        print("Creating Browser wrapper...")
        browser = Browser(driver, anticaptcha_manual_install=False)
        
        print("Navigating to Google...")
        browser.go_to("https://www.google.com")
        time.sleep(2)
        
        print("Taking screenshot...")
        screenshot_path = "api_test_screenshot.png"
        browser.screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Get some page info
        title = browser.get_page_title()
        print(f"Page title: {title}")
        
        # Test cleanup
        print("Cleaning up browser...")
        driver.quit()
        
        print("\n✅ Chrome test in API context succeeded!")
        return True
    except Exception as e:
        print(f"\n❌ Chrome test in API context failed: {str(e)}")
        return False
        
if __name__ == "__main__":
    success = test_chrome_in_api()
    
    if success:
        print("\nNow the Chrome browser works! You can update api.py with the browser.py changes.")
        print("The fix we made was to simplify Chrome options and bypass SSL verification.")
        sys.exit(0)
    else:
        print("\nThe Chrome browser still has issues. Further debugging needed.")
        print("Try manually opening Chrome to check if it works normally.")
        sys.exit(1) 