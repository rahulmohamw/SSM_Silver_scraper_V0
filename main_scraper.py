#!/usr/bin/env python3
"""
Test script for SMM Silver Price Scraper
Use this to test the scraper locally before deploying
"""

import os
import sys
import time
from datetime import datetime
from main_scraper import SMMSilverScraper

def test_scraper():
    """Test the scraper functionality"""
    print("🧪 Testing SMM Silver Price Scraper")
    print("=" * 50)
    
    # Create test instance
    scraper = SMMSilverScraper()
    
    print(f"📁 Testing directory creation...")
    scraper.ensure_directories()
    
    # Check if directories exist
    required_dirs = ['csv', 'screenshots', 'logs']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
    
    print(f"\n🚀 Running scraper test...")
    start_time = time.time()
    
    try:
        success = scraper.run_scraper()
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ Test completed in {duration:.2f} seconds")
        
        if success:
            print("✅ Scraper test PASSED")
        else:
            print("❌ Scraper test FAILED")
            
        # Check generated files
        print(f"\n📊 Checking generated files...")
        
        # CSV files
        csv_files = [f for f in os.listdir('csv') if f.endswith('.csv')]
        if csv_files:
            print(f"✅ CSV files generated: {len(csv_files)}")
            for file in csv_files:
                file_path = os.path.join('csv', file)
                size = os.path.getsize(file_path)
                print(f"   📄 {file} ({size} bytes)")
                
                # Read and display CSV content
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        print(f"   Content preview:\n   {content[:200]}...")
                except:
                    pass
        else:
            print("❌ No CSV files generated")
        
        # Screenshot files
        screenshot_files = [f for f in os.listdir('screenshots') if f.endswith(('.png', '.jpg'))]
        if screenshot_files:
            print(f"✅ Screenshot files generated: {len(screenshot_files)}")
            for file in screenshot_files:
                file_path = os.path.join('screenshots', file)
                size = os.path.getsize(file_path)
                print(f"   📸 {file} ({size} bytes)")
        else:
            print("❌ No screenshot files generated")
        
        # Log files
        log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
        if log_files:
            print(f"✅ Log files generated: {len(log_files)}")
            for file in log_files:
                file_path = os.path.join('logs', file)
                size = os.path.getsize(file_path)
                print(f"   📝 {file} ({size} bytes)")
        else:
            print("❌ No log files generated")
        
        # Check for page source
        if os.path.exists('logs/page_source.html'):
            size = os.path.getsize('logs/page_source.html')
            print(f"✅ Page source saved: page_source.html ({size} bytes)")
        else:
            print("❌ Page source not saved")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_dependencies():
    """Test if all dependencies are available"""
    print("🔍 Testing dependencies...")
    
    dependencies = [
        'selenium',
        'webdriver_manager',
        'pandas',
        'requests'
    ]
    
    all_good = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Not installed")
            all_good = False
    
    # Test Chrome availability
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        
        # Just test driver creation, don't navigate
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.quit()
        print("✅ Chrome WebDriver")
        
    except Exception as e:
        print(f"❌ Chrome WebDriver - {str(e)}")
        all_good = False
    
    return all_good

def show_results():
    """Display results in a formatted way"""
    print("\n" + "=" * 50)
    print("📊 SCRAPER TEST RESULTS")
    print("=" * 50)
    
    # Show CSV data
    csv_files = [f for f in os.listdir('csv') if f.endswith('.csv')]
    if csv_files:
        latest_csv = max(csv_files, key=lambda x: os.path.getctime(os.path.join('csv', x)))
        print(f"\n📄 Latest CSV: {latest_csv}")
        try:
            import pandas as pd
            df = pd.read_csv(os.path.join('csv', latest_csv))
            print(df.to_string(index=False))
        except:
            # Fallback to basic file reading
            with open(os.path.join('csv', latest_csv), 'r') as f:
                print(f.read())
    
    # Show file sizes
    print(f"\n📁 File Summary:")
    for folder in ['csv', 'screenshots', 'logs']:
        if os.path.exists(folder):
            files = os.listdir(folder)
            total_size = sum(os.path.getsize(os.path.join(folder, f)) for f in files)
            print(f"   {folder}/: {len(files)} files, {total_size:,} bytes")

def main():
    """Main test function"""
    print("🥈 SMM Silver Price Scraper - Test Suite")
    print("=" * 50)
    
    # Test 1: Dependencies
    print("\n1️⃣ Testing Dependencies...")
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dependency test failed. Please install missing packages:")
        print("pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies available!")
    
    # Test 2: Scraper functionality
    print("\n2️⃣ Testing Scraper...")
    scraper_ok = test_scraper()
    
    # Test 3: Show results
    if scraper_ok:
        show_results()
        
        print(f"\n🎉 Test completed successfully!")
        print(f"💡 Your scraper is ready for GitHub Actions deployment")
        print(f"📋 Next steps:")
        print(f"   1. git add .")
        print(f"   2. git commit -m 'Updated scraper with improvements'")
        print(f"   3. git push origin main")
        print(f"   4. Check GitHub Actions tab for automated runs")
    else:
        print(f"\n❌ Test failed. Check the logs for details.")
        print(f"📋 Troubleshooting tips:")
        print(f"   - Check internet connection")
        print(f"   - Verify Chrome is installed")
        print(f"   - Check logs/scraper.log for detailed error info")
        
    return scraper_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
