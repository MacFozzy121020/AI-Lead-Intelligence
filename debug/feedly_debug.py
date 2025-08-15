import requests
import json
from datetime import datetime

def test_feedly_connection():
    """
    Test Feedly connection and show what feeds are available
    """
    # Your Feedly access token
    feedly_access_token = "eyJraWQiOiJhdXQiLCJ2IjoiMSIsImFsZyI6ImRpciIsImVuYyI6IkEyNTZHQ00ifQ..TX_hdbfccAc7cOkz.qNP2tnP1SrOvv9bf4QV5JvSqCBX2cOUkT5v2ELlZm-s0wYStHTBlwyoEIV8P9bRW44WN5adfYiPsCnZGUl7WIPipF7NBqjgiT_G4UvJ5tFg_Y5WXUJo-kopu_mqhJR0N8NkPXpq4qgdoVtlQARUIK8D9kCpEYfk6T1HvxWIR5E0EWwiyf7JgXb8cGNhoya2JQ1S7J6bjhWJJeqpGiOy8z_hkp3lpXvxNrir536VORrWxVsl8eA.OlwGvz9sezIEAT9x6zDwtQ"
    
    feedly_api_base = "https://cloud.feedly.com/v3"
    
    headers = {'Authorization': f'Bearer {feedly_access_token}'}
    
    print("🔧 FEEDLY CONNECTION DIAGNOSTIC")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("1. Testing Feedly API connection...")
    try:
        response = requests.get(f"{feedly_api_base}/profile", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Connection successful!")
        else:
            print(f"   ❌ Connection failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get subscriptions
    print("\n2. Getting your Feedly subscriptions...")
    try:
        subs_response = requests.get(f"{feedly_api_base}/subscriptions", headers=headers)
        print(f"   Status: {subs_response.status_code}")
        
        if subs_response.status_code == 200:
            subscriptions = subs_response.json()
            print(f"   ✅ Found {len(subscriptions)} subscriptions")
            
            print("\n📰 YOUR CURRENT FEEDS:")
            for i, sub in enumerate(subscriptions, 1):
                title = sub.get('title', 'No title')
                feed_id = sub.get('id', 'No ID')
                print(f"   {i:2d}. {title}")
                
        else:
            print(f"   ❌ Failed to get subscriptions: {subs_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error getting subscriptions: {e}")
        return
    
    # Test 3: Get articles from first feed
    print("\n3. Testing article retrieval from first feed...")
    try:
        if subscriptions:
            first_feed = subscriptions[0]
            feed_title = first_feed.get('title', 'Unknown')
            feed_id = first_feed.get('id', '')
            
            print(f"   Testing feed: {feed_title}")
            
            params = {
                'streamId': feed_id,
                'count': 5
            }
            
            articles_response = requests.get(
                f"{feedly_api_base}/streams/contents",
                headers=headers,
                params=params
            )
            
            print(f"   Status: {articles_response.status_code}")
            
            if articles_response.status_code == 200:
                data = articles_response.json()
                items = data.get('items', [])
                print(f"   ✅ Found {len(items)} recent articles")
                
                if items:
                    print("\n📄 SAMPLE ARTICLES:")
                    for i, item in enumerate(items[:3], 1):
                        title = item.get('title', 'No title')
                        published = item.get('published', 0)
                        if published:
                            pub_date = datetime.fromtimestamp(published/1000).strftime('%d %B %Y')
                        else:
                            pub_date = 'No date'
                        print(f"   {i}. {title}")
                        print(f"      Published: {pub_date}")
                        print()
                else:
                    print("   ⚠️  No articles found in this feed")
            else:
                print(f"   ❌ Failed to get articles: {articles_response.text}")
        
    except Exception as e:
        print(f"   ❌ Error getting articles: {e}")
    
    # Test 4: Check for startup-specific feeds
    print("\n4. Checking for startup/SME focused feeds...")
    startup_keywords = ['startup', 'small business', 'sme', 'entrepreneur', 'scottish business', 'growth']
    startup_feeds = []
    
    for sub in subscriptions:
        title = sub.get('title', '').lower()
        if any(keyword in title for keyword in startup_keywords):
            startup_feeds.append(sub.get('title', 'Unknown'))
    
    if startup_feeds:
        print(f"   ✅ Found {len(startup_feeds)} startup/SME focused feeds:")
        for feed in startup_feeds:
            print(f"      • {feed}")
    else:
        print("   ⚠️  No obvious startup/SME feeds found")
        print("   💡 Consider adding more startup-focused RSS feeds to Feedly")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")

if __name__ == "__main__":
    test_feedly_connection()