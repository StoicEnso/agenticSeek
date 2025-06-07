#!/usr/bin/env python3

import os
import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

def test_undetected_chrome():
    """Test Chrome with undetected-chromedriver"""
    print("Testing Chrome with undetected-chromedriver...")
    
    try:
        print("Configuring Chrome options...")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1200,800")
        
        # Disable headless mode completely
        print("Starting Chrome in visible mode...")
        driver = uc.Chrome(options=options)
        
        print("✓ Chrome started successfully!")
        time.sleep(2)  # Wait for browser to fully initialize
        
        # Test navigation
        print("Navigating to Google...")
        driver.get("https://www.google.com")
        time.sleep(3)  # Wait for page to load
        
        print(f"Page title: {driver.title}")
        
        # Take screenshot
        screenshot_path = "undetected_test.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Clean up
        driver.quit()
        print("Test passed successfully!")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Undetected ChromeDriver Test")
    print("===========================")
    
    result = test_undetected_chrome()
    
    if result:
        print("\nSuccess! Chrome started with undetected-chromedriver")
        sys.exit(0)
    else:
        print("\nFailed to start Chrome with undetected-chromedriver")
        print("\nTroubleshooting tips:")
        print("1. Make sure Chrome is closed before running this test")
        print("2. Check your macOS security settings")
        print("3. Make sure you have the right version of undetected-chromedriver")
        print("4. Try with a completely fresh Chrome profile")
        sys.exit(1) 