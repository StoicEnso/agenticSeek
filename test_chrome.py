#!/usr/bin/env python3

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def get_chrome_path():
    """Get the path to the Chrome executable."""
    if sys.platform.startswith("darwin"):  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
        ]
    elif sys.platform.startswith("win"):
        paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe")
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/opt/chrome/chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]

    for path in paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    print("Chrome not found in common locations. Please provide path manually.")
    return None

def test_chrome():
    """Test Chrome initialization with different options."""
    try:
        print("Testing Chrome initialization...")
        
        # Install chromedriver if needed
        chromedriver_path = chromedriver_autoinstaller.install()
        print(f"Using ChromeDriver at: {chromedriver_path}")
        
        # Get Chrome path
        chrome_path = get_chrome_path()
        if not chrome_path:
            print("ERROR: Chrome executable not found!")
            return False
        print(f"Using Chrome at: {chrome_path}")
        
        # Basic Chrome options
        options = Options()
        options.binary_location = chrome_path
        
        # Test with various configurations
        configs = [
            {"name": "Basic (non-headless)", "headless": False},
            {"name": "Headless", "headless": True}
        ]
        
        for config in configs:
            print(f"\nTesting {config['name']} mode...")
            options = Options()
            options.binary_location = chrome_path
            
            if config["headless"]:
                options.add_argument("--headless=new")
                
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            try:
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
                
                print(f"✅ Successfully created Chrome driver with {config['name']} configuration")
                print(f"Browser version: {driver.capabilities['browserVersion']}")
                print(f"Driver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
                
                # Try to navigate to a website
                driver.get("https://www.google.com")
                print(f"✅ Successfully navigated to Google")
                print(f"Page title: {driver.title}")
                
                # Take a screenshot
                screenshot_path = f"chrome_test_{config['name'].replace(' ', '_').lower()}.png"
                driver.save_screenshot(screenshot_path)
                print(f"✅ Screenshot saved to {screenshot_path}")
                
                # Clean up
                driver.quit()
                print(f"✅ {config['name']} mode works!")
            except Exception as e:
                print(f"❌ {config['name']} mode failed: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error in test_chrome: {str(e)}")
        return False

if __name__ == "__main__":
    print("Chrome/Selenium Test Script")
    print("===========================")
    result = test_chrome()
    if result:
        print("\nAt least one Chrome configuration works!")
        sys.exit(0)
    else:
        print("\nAll Chrome configurations failed!")
        sys.exit(1) 