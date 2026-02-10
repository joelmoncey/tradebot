from growwapi import GrowwAPI
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        print("\n--- Testing Groww Connection ---")
        
        # 1. Initialize
        print(f"Using Auth Token: {Config.GROWW_AUTH_TOKEN[:5]}... (masked)")
        groww = GrowwAPI(Config.GROWW_API_KEY, Config.GROWW_API_SECRET)
        groww.set_access_token(Config.GROWW_AUTH_TOKEN)
        print("Authentication initialized.")

        # 2. Check Balance (Good way to verify auth)
        print("\nAttempting to search for 'RELIANCE' to verify API...")
        results = groww.search_scrip("RELIANCE")
        
        if results and len(results) > 0:
            print(f"Success! Found {len(results)} results.")
            print(f"First result: {results[0].get('displayName')} (ID: {results[0].get('searchId')})")
        else:
            print("Auth seems okay, but no results found for 'RELIANCE'.")

        # 3. Test Option Search
        print("\nAttempting to search for 'NIFTY 26100 PE' (Example)...")
        results = groww.search_scrip("NIFTY 26100 PE")
        
        if results and len(results) > 0:
             print(f"Success! Found option: {results[0].get('displayName')} (ID: {results[0].get('searchId')})")
        else:
            print("No results for 'NIFTY 26100 PE'. Try full expiry name like 'NIFTY 21SEP 26100 PE'")

    except Exception as e:
        print(f"\n[ERROR] Connection Failed: {e}")
        print("Please check your GROWW_AUTH_TOKEN in .env")

if __name__ == "__main__":
    test_connection()
