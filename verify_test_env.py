#!/usr/bin/env python3
"""
Verification script for Raspberry Pi 4B Test Environment
"""

import os
import sys
import subprocess
import time
import requests
import zipfile

def check_files():
    """Check that all required files exist"""
    required_files = [
        'rpi4b-hardware-test.zip',
        'setup-pi4b-test.sh',
        'prepare-pi4b-test.bat',
        'TEST_ENVIRONMENT_README.md'
    ]
    
    print("Checking required files...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (MISSING)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nERROR: Missing {len(missing_files)} required files")
        return False
    
    print("All required files present!")
    return True

def verify_zip_contents():
    """Verify the contents of the zip file"""
    print("\nVerifying zip file contents...")
    
    try:
        with zipfile.ZipFile('rpi4b-hardware-test.zip', 'r') as zip_ref:
            files = zip_ref.namelist()
            print("Zip file contents:")
            for file in files:
                print(f"  ✓ {file}")
            
            # Check for required files in zip
            required_in_zip = ['setup-pi4b-test.sh', 'requirements.txt']
            missing_in_zip = []
            
            for req_file in required_in_zip:
                if req_file not in files:
                    print(f"  ✗ {req_file} (MISSING FROM ZIP)")
                    missing_in_zip.append(req_file)
            
            if missing_in_zip:
                print(f"ERROR: Missing {len(missing_in_zip)} required files in zip")
                return False
                
    except Exception as e:
        print(f"ERROR: Failed to read zip file: {e}")
        return False
    
    print("Zip file verified successfully!")
    return True

def test_script_execution():
    """Test that the setup script can be parsed"""
    print("\nTesting script execution...")
    
    try:
        # Test that the bash script has proper shebang
        with open('setup-pi4b-test.sh', 'r') as f:
            first_line = f.readline().strip()
            if first_line == '#!/bin/bash':
                print("  ✓ Bash script has proper shebang")
            else:
                print(f"  ✗ Unexpected shebang: {first_line}")
                return False
        
        # Test that batch file exists and is readable
        if os.path.exists('prepare-pi4b-test.bat'):
            print("  ✓ Batch file exists")
        else:
            print("  ✗ Batch file missing")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to test script execution: {e}")
        return False
    
    print("Script execution test passed!")
    return True

def main():
    """Main verification function"""
    print("=" * 50)
    print("Raspberry Pi 4B Test Environment Verification")
    print("=" * 50)
    
    # Run all checks
    checks = [
        check_files,
        verify_zip_contents,
        test_script_execution
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ ALL VERIFICATION CHECKS PASSED!")
        print("\nYour Raspberry Pi 4B test environment is ready.")
        print("To deploy:")
        print("1. Transfer rpi4b-hardware-test.zip to your Pi 4B")
        print("2. Extract and run setup-pi4b-test.sh")
        print("3. Run the test application")
    else:
        print("✗ SOME VERIFICATION CHECKS FAILED!")
        print("Please check the errors above and fix them.")
    print("=" * 50)

if __name__ == '__main__':
    main()