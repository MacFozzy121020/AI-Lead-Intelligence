import requests
import json

def check_feedly_pro_status():
    """
    Check if Feedly Pro is active and what your rate limits are
    """
    # Your fresh Feedly Pro access token
    feedly_access_token = "eyJraWQiOiJhdXQiLCJ2IjoiMSIsImFsZyI6ImRpciIsImVuYyI6IkEyNTZHQ00ifQ..5zpU8IXOd2kWPJTW.3zSPbXJzfb8IlBEhz29IgyxZbYHP3sedFRQYWklsqConiFabBc5WBkMazmQ8Tx9JMZc-e7BBMRwAJGW_aMtBTFEiaWbUaJlaKyEMha9jK-TiLJQjJkk6rHRSQ_Tn51766wgnR0iRAAC1jp5IF5GTRJroEiKXlAK52U2xLVBN3R8wE6aNFthA2_wcfOLYEOC3lq5YrqY5ufGHzzvTdEXNOA53RAjjv_gdcKeiuTO5XRfQWQd7Fw.7dwB9XIxgcJyT05QC6xEIg"
    
    feedly_api_base = "https://cloud.feedly.com/v3"
    headers = {'Authorization': f'Bearer {feedly_access_token}'}
    
    print("🔍 FEEDLY PRO ACCOUNT STATUS CHECK")
    print("=" * 50)
    
    # Check profile for Pro status
    print("1. Checking account profile and subscription status...")
    try:
        profile_response = requests.get(f"{feedly_api_base}/profile", headers=headers)
        print(f"   Status Code: {profile_response.status_code}")
        
        if profile_response.status_code == 429:
            print("   ❌ Still hitting rate limits")
            print("   💡 This suggests Pro features haven't activated yet")
            
            # Check the response headers for rate limit info
            headers_info = profile_response.headers
            print("\n📊 RATE LIMIT HEADERS:")
            for key, value in headers_info.items():
                if 'limit' in key.lower() or 'rate' in key.lower():
                    print(f"   {key}: {value}")
            
            error_response = profile_response.json()
            print(f"\n❌ Error details: {error_response}")
            
            reset_time = error_response.get('errorMessage', '')
            if 'reset in' in reset_time:
                seconds = reset_time.split('reset in ')[1].split('s')[0]
                hours = int(seconds) // 3600
                print(f"\n⏰ Rate limit resets in: {hours} hours")
            
            return False
            
        elif profile_response.status_code == 200:
            profile_data = profile_response.json()
            print("   ✅ API call successful!")
            
            # Check for Pro indicators
            print(f"\n👤 ACCOUNT INFO:")
            print(f"   User ID: {profile_data.get('id', 'Not found')}")
            print(f"   Email: {profile_data.get('email', 'Not found')}")
            
            # Look for subscription info
            if 'subscription' in profile_data:
                sub_info = profile_data['subscription']
                print(f"   Subscription: {sub_info}")
            
            # Check if there are any pro-specific fields
            pro_indicators = ['pro', 'premium', 'subscription', 'plan']
            for key, value in profile_data.items():
                if any(indicator in key.lower() for indicator in pro_indicators):
                    print(f"   {key}: {value}")
            
            return True
        else:
            print(f"   ❌ Unexpected status: {profile_response.status_code}")
            print(f"   Response: {profile_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def get_fresh_pro_token_instructions():
    """
    Instructions for getting a fresh Pro token
    """
    print("\n🔄 GET FRESH PRO TOKEN:")
    print("=" * 30)
    print("1. Go to: https://feedly.com/v3/auth/dev")
    print("2. Make sure you're logged into your PRO account")
    print("3. Look for your subscription status on the page")
    print("4. Click 'Get your access token'")
    print("5. Copy the new token")
    print("6. Replace the token in your scripts")
    print("\n💡 Pro tokens might look different or have additional permissions")

def test_with_fresh_token():
    """
    Function to test with a fresh token
    """
    print("\n🔧 FRESH TOKEN TEST:")
    print("=" * 25)
    new_token = input("Paste your fresh Pro token here (or press Enter to skip): ").strip()
    
    if not new_token:
        print("Skipping fresh token test")
        return
    
    headers = {'Authorization': f'Bearer {new_token}'}
    
    try:
        response = requests.get("https://cloud.feedly.com/v3/profile", headers=headers)
        print(f"Fresh token test status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Fresh token works!")
            print("💡 Update your scripts with this new token")
        elif response.status_code == 429:
            print("❌ Still rate limited with fresh token")
            print("💡 Pro features may not be active yet - try again in a few hours")
        else:
            print(f"❌ Fresh token error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing fresh token: {e}")

if __name__ == "__main__":
    # Check current status
    success = check_feedly_pro_status()
    
    if not success:
        print("\n💡 RECOMMENDATIONS:")
        print("1. Get a fresh token from your Pro account")
        print("2. Wait a few hours for Pro features to activate")
        print("3. Contact Feedly support if issues persist")
        
        get_fresh_pro_token_instructions()
        test_with_fresh_token()
    else:
        print("\n✅ Account appears to be working!")
        print("You should be able to run your lead intelligence system now.")
        print("\nTry running: python precision_leads.py")