#!/usr/bin/env python3

import os
import sys
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import subprocess

def check_chrome_version():
    """Check the installed Chrome version"""
    if sys.platform.startswith("darwin"):  # macOS
        try:
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            output = subprocess.check_output([chrome_path, "--version"]).decode("utf-8")
            print(f"Installed Chrome: {output.strip()}")
        except:
            print("Could not determine Chrome version")

def test_chrome():
    """Test minimal Chrome initialization"""
    print("Testing Chrome with minimal settings...")
    check_chrome_version()
    
    # Create options with enhanced macOS settings
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Create a persistent data directory
    data_dir = tempfile.mkdtemp()
    print(f"Using temporary data directory: {data_dir}")
    options.add_argument(f"--user-data-dir={data_dir}")
    
    # Add macOS specific options
    if sys.platform.startswith("darwin"):
        print("Detected macOS - adding platform-specific options")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=Translate")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--window-size=1200,800")
    
    # Try with non-headless mode
    try:
        print("\nAttempting to start Chrome in non-headless mode...")
        driver = webdriver.Chrome(options=options)
        print("✓ Chrome started successfully!")
        print(f"Chrome version: {driver.capabilities['browserVersion']}")
        
        # Wait a moment for the browser to fully initialize
        time.sleep(2)
        
        # Test navigation
        print("Navigating to Google...")
        driver.get("https://www.google.com")
        
        # Wait for page to load
        time.sleep(3)
        print(f"Page title: {driver.title}")
        
        # Take screenshot
        screenshot_path = "chrome_test.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Clean up
        driver.quit()
        print("Chrome test passed successfully!")
        return True
    except Exception as e:
        print(f"✗ Error starting Chrome: {str(e)}")
        
    return False

if __name__ == "__main__":
    print("Chrome Test Script")
    print("=================")
    result = test_chrome()
    
    if result:
        print("\nChrome started successfully!")
        sys.exit(0)
    else:
        print("\nFailed to start Chrome browser.")
        print("Troubleshooting tips:")
        print("1. Make sure Chrome is installed")
        print("2. Try running with --no-cache flag")
        print("3. Make sure your macOS security settings allow Chrome to be controlled")
        print("4. Try updating ChromeDriver: python -m pip install --upgrade chromedriver-autoinstaller")
        print("5. Make sure Chrome is not already running with remote debugging port 9222")
        sys.exit(1) 