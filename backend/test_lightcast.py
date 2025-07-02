#!/usr/bin/env python3
"""Test script to verify Lightcast API connection and occupation data fetching."""

import os
import json
from dotenv import load_dotenv
from pyghtcast import lightcast

# Load environment variables
load_dotenv()

# Get credentials
username = os.getenv("LCAPI_USER")
password = os.getenv("LCAPI_PASS")

print("Testing Lightcast API connection...")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'None'}")

try:
    # Initialize the client
    client = lightcast.Lightcast(username=username, password=password)
    print("\n✓ Successfully initialized Lightcast client")
    
    # Try to get occupation data
    print("\nAttempting to fetch occupation data...")
    
    # First, let's explore what datasets are available
    # This is a test query to understand the API structure
    try:
        # Try different approaches based on pyghtcast documentation
        
        # Approach 1: Try to query occupation taxonomy directly
        query = client.build_query_corelmi(
            cols=['soc', 'title'],
            constraints=[]
        )
        print(f"\nBuilt query: {json.dumps(query, indent=2)}")
        
        # Try different dataset names
        dataset_names = ['us.occupations', 'occupations', 'soc', 'occupation_taxonomy']
        
        for dataset in dataset_names:
            try:
                print(f"\nTrying dataset: {dataset}")
                results = client.query_corelmi(dataset, query)
                print(f"✓ Success with dataset: {dataset}")
                print(f"Results type: {type(results)}")
                if isinstance(results, dict):
                    print(f"Keys: {list(results.keys())}")
                    if 'data' in results:
                        print(f"Data length: {len(results.get('data', []))}")
                        if results['data']:
                            print(f"First item: {results['data'][0]}")
                break
            except Exception as e:
                print(f"✗ Failed with dataset '{dataset}': {str(e)}")
                
    except Exception as e:
        print(f"\n✗ Failed to build/execute query: {str(e)}")
        print("\nTrying alternative approach...")
        
        # Alternative: Try to inspect available methods
        print(f"\nAvailable client methods: {[m for m in dir(client) if not m.startswith('_')]}")
        
except Exception as e:
    print(f"\n✗ Failed to connect to Lightcast API: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    
print("\nTest complete.")