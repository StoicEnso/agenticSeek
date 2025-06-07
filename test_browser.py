#!/usr/bin/env python3

import os
import sys
import configparser
from sources.browser import Browser, create_driver
from sources.utility import pretty_print

def test_browser_initialization():
    """Test browser initialization with different configurations."""
    print("Testing browser initialization...")
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    languages = config["MAIN"]["languages"].split(' ')
    
    # Try different browser configurations
    configurations = [
        {"headless": False, "stealth_mode": False, "name": "Non-headless, non-stealth"},
        {"headless": True, "stealth_mode": False, "name": "Headless, non-stealth"},
        {"headless": False, "stealth_mode": True, "name": "Non-headless, stealth"},
        {"headless": True, "stealth_mode": True, "name": "Headless, stealth"}
    ]
    
    for cfg in configurations:
        print(f"\nTrying {cfg['name']} mode...")
        try:
            driver = create_driver(
                headless=cfg["headless"], 
                stealth_mode=cfg["stealth_mode"], 
                lang=languages[0]
            )
            browser = Browser(driver, anticaptcha_manual_install=cfg["stealth_mode"])
            print(f"✅ {cfg['name']} mode works!")
            
            # Take a screenshot to verify it's working
            browser.screenshot("test_screenshot.png")
            print(f"Screenshot saved as test_screenshot.png")
            
            # Clean up
            browser.driver.quit()
            
            # First working configuration is enough
            return True
        except Exception as e:
            print(f"❌ {cfg['name']} mode failed: {str(e)}")
    
    print("\nAll browser configurations failed.")
    return False

if __name__ == "__main__":
    success = test_browser_initialization()
    if success:
        print("\nBrowser test successful! At least one configuration works.")
        sys.exit(0)
    else:
        print("\nBrowser test failed! Please check your Chrome installation and ChromeDriver.")
        print("You might need to manually install ChromeDriver that matches your Chrome version.")
        print("See: https://chromedriver.chromium.org/downloads")
        sys.exit(1) 