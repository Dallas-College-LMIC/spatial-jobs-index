#!/usr/bin/env python3
"""Test script to verify Lightcast API integration."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.lightcast_service import get_lightcast_service

def test_lightcast_connection():
    """Test the Lightcast API connection and data retrieval."""
    print("Testing Lightcast API integration...")
    
    try:
        # Get the service instance
        service = get_lightcast_service()
        print("✓ Successfully created Lightcast service")
        
        # Try to fetch occupations
        print("\nFetching occupations from Lightcast API...")
        occupations = service.get_occupations_with_names()
        
        if occupations:
            print(f"✓ Successfully fetched {len(occupations)} occupations")
            print("\nSample occupations:")
            for occ in occupations[:5]:
                print(f"  - {occ['code']}: {occ['name']}")
        else:
            print("✗ No occupations returned from API")
            
        # Test specific occupation lookup
        test_code = "11-1021"
        print(f"\nLooking up occupation {test_code}...")
        specific_occ = service.get_occupation_by_code(test_code)
        if specific_occ:
            print(f"✓ Found: {specific_occ['code']} - {specific_occ['name']}")
        else:
            print(f"✗ Occupation {test_code} not found")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_lightcast_connection()
    sys.exit(0 if success else 1)