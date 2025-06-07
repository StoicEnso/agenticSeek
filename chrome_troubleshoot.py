#!/usr/bin/env python3

import os
import sys
import ssl
import platform
import subprocess
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sources.browser import create_driver, Browser
import configparser
import time
import shutil

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_success(text):
    """Print a success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print an error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print an info message"""
    print(f"ℹ️ {text}")

def run_shell_command(command):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                                capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def check_chrome_version():
    """Check Chrome version on the system"""
    print_header("Checking Chrome Version")
    
    system = platform.system()
    if system == "Darwin":  # macOS
        cmd = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version"
    elif system == "Windows":
        cmd = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
    else:  # Linux
        cmd = "google-chrome --version"
    
    version_output = run_shell_command(cmd)
    print_info(f"Chrome version: {version_output}")
    return version_output

def check_chromedriver():
    """Check ChromeDriver installation"""
    print_header("Checking ChromeDriver")
    
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print_info("Using webdriver_manager to get ChromeDriver info")
        driver_path = ChromeDriverManager().install()
        print_success(f"ChromeDriver found at: {driver_path}")
        return driver_path
    except Exception as e:
        print_error(f"Error checking ChromeDriver: {str(e)}")
        return None

def test_chrome_minimal():
    """Test Chrome with minimal options"""
    print_header("Testing Chrome with Minimal Options")
    
    try:
        # Bypass SSL certificate verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print_info("Initializing Chrome with minimal options...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print_info("Navigating to Google...")
        driver.get("https://www.google.com")
        title = driver.title
        print_success(f"Page loaded successfully! Title: {title}")
        
        driver.quit()
        return True
    except Exception as e:
        print_error(f"Error with minimal Chrome options: {str(e)}")
        traceback.print_exc()
        return False

def test_chrome_with_profile():
    """Test Chrome with a fresh profile"""
    print_header("Testing Chrome with Fresh Profile")
    
    temp_profile = os.path.join(os.getcwd(), "temp_chrome_profile")
    if os.path.exists(temp_profile):
        shutil.rmtree(temp_profile)
    os.makedirs(temp_profile)
    
    try:
        # Bypass SSL certificate verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={temp_profile}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print_info("Initializing Chrome with fresh profile...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print_info("Navigating to Google...")
        driver.get("https://www.google.com")
        title = driver.title
        print_success(f"Page loaded successfully! Title: {title}")
        
        driver.quit()
        return True
    except Exception as e:
        print_error(f"Error with Chrome profile: {str(e)}")
        return False
    finally:
        if os.path.exists(temp_profile):
            shutil.rmtree(temp_profile)

def test_with_browser_py():
    """Test with our sources/browser.py implementation"""
    print_header("Testing with browser.py implementation")
    
    try:
        # Bypass SSL certificate verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        print_info("Creating driver with browser.py...")
        driver = create_driver(headless=False, stealth_mode=False)
        browser = Browser(driver, anticaptcha_manual_install=False)
        
        print_info("Navigating to Google...")
        driver.get("https://www.google.com")
        title = driver.title
        print_success(f"Page loaded successfully! Title: {title}")
        
        driver.quit()
        return True
    except Exception as e:
        print_error(f"Error with browser.py: {str(e)}")
        return False

def check_config():
    """Check and optionally update config.ini"""
    print_header("Checking config.ini")
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if not config.has_section('BROWSER'):
        print_error("No BROWSER section in config.ini")
        return False
    
    headless = config.getboolean('BROWSER', 'headless_browser', fallback=None)
    if headless is None:
        print_error("No headless_browser setting in config.ini")
        return False
    
    print_info(f"Current headless_browser setting: {headless}")
    
    if headless:
        print_info("Setting headless_browser to False for better compatibility")
        config.set('BROWSER', 'headless_browser', 'False')
        with open('config.ini', 'w') as f:
            config.write(f)
        print_success("Updated config.ini with headless_browser = False")
    else:
        print_success("headless_browser already set to False")
    
    return True

def apply_fixes():
    """Apply all known fixes"""
    print_header("Applying All Fixes")
    
    # Create a backup of browser.py
    browser_path = "sources/browser.py"
    backup_path = "sources/browser.py.bak"
    
    if os.path.exists(browser_path) and not os.path.exists(backup_path):
        shutil.copy(browser_path, backup_path)
        print_success(f"Created backup of browser.py at {backup_path}")
    
    # Apply fixes to browser.py
    try:
        with open(browser_path, 'r') as f:
            content = f.read()
        
        # Check if SSL fix is already applied
        if "ssl._create_default_https_context" not in content:
            ssl_fix = "import ssl\nssl._create_default_https_context = ssl._create_unverified_context\n\n"
            
            # Find the right spot to add the import (after other imports, before classes/functions)
            import_section_end = content.find("class Browser:")
            if import_section_end == -1:
                import_section_end = content.find("def create_driver")
            
            if import_section_end != -1:
                content = content[:import_section_end] + ssl_fix + content[import_section_end:]
                print_success("Added SSL certificate verification bypass")
        else:
            print_info("SSL certificate verification bypass already present")
        
        # Update create_driver function to use minimal options
        if "def create_driver(" in content:
            start_idx = content.find("def create_driver(")
            if start_idx != -1:
                end_idx = content.find("def ", start_idx + 1)
                if end_idx == -1:  # If it's the last function
                    end_idx = len(content)
                
                func_content = content[start_idx:end_idx]
                
                # Check if function is already fixed
                if "Initializing Chrome browser with minimal settings" not in func_content:
                    new_func = """def create_driver(headless=False, stealth_mode=False, lang="en-US"):
    print("Initializing Chrome browser with minimal settings...")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create a temporary user data directory for each session
    import tempfile
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    
    # Set language if provided
    if lang:
        chrome_options.add_argument(f"--lang={lang}")
    
    # Configure headless mode if requested
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Create and return the Chrome driver
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome initialized successfully!")
        return driver
    except Exception as e:
        print(f"Error initializing Chrome: {str(e)}")
        raise
"""
                    content = content[:start_idx] + new_func + content[end_idx:]
                    print_success("Updated create_driver function with minimal settings")
                else:
                    print_info("create_driver function already has minimal settings")
        
        # Write the updated content back to the file
        with open(browser_path, 'w') as f:
            f.write(content)
        
        print_success("Applied all fixes to browser.py")
        return True
    except Exception as e:
        print_error(f"Error applying fixes: {str(e)}")
        return False

def run_test():
    """Run a full test of the API initialization"""
    print_header("Running API Initialization Test")
    
    try:
        # Try importing and running our test
        from api_init_test import test_api_init
        
        success = test_api_init()
        if success:
            print_success("API initialization test passed!")
        else:
            print_error("API initialization test failed.")
        
        return success
    except ImportError:
        print_error("api_init_test.py not found or couldn't be imported")
        return False
    except Exception as e:
        print_error(f"Error running API initialization test: {str(e)}")
        return False

def main():
    print_header("Chrome Troubleshooting Tool")
    print("This tool will check and fix Chrome-related issues in AgenticSeek")
    
    # Check system information
    system = platform.system()
    print_info(f"Operating System: {platform.platform()}")
    print_info(f"Python Version: {platform.python_version()}")
    
    # Run checks
    check_chrome_version()
    check_chromedriver()
    check_config()
    
    # Run tests
    minimal_success = test_chrome_minimal()
    profile_success = test_chrome_with_profile()
    browser_py_success = test_with_browser_py()
    
    # Apply fixes if needed
    if not (minimal_success and profile_success and browser_py_success):
        print_header("Applying Fixes")
        user_input = input("Would you like to apply all recommended fixes? (y/n): ").strip().lower()
        
        if user_input == 'y':
            apply_fixes()
            
            # Run test again to see if fixes worked
            print_info("Running tests again with fixes applied...")
            test_with_browser_py()
            run_test()
        else:
            print_info("Skipping automatic fixes")
    else:
        print_success("All Chrome tests passed! No fixes needed.")
    
    # Summary
    print_header("Troubleshooting Summary")
    print_info("Chrome minimal test: " + ("✅ Passed" if minimal_success else "❌ Failed"))
    print_info("Chrome profile test: " + ("✅ Passed" if profile_success else "❌ Failed"))
    print_info("browser.py test: " + ("✅ Passed" if browser_py_success else "❌ Failed"))
    
    if minimal_success and profile_success and browser_py_success:
        print_success("All tests passed. Chrome should work with AgenticSeek!")
    else:
        print_info("Some tests failed. If you applied fixes, try running the API again.")
        print_info("If issues persist, check the GitHub issues or community forums for help.")

if __name__ == "__main__":
    main() 