"""Debug test to see the actual error."""
import pytest


def test_debug_endpoint_error(test_client, test_session):
    """Debug test to see what error is causing 500."""
    # Make request
    response = test_client.get("/occupation_ids")
    
    # Print full response
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        # Try to get more details
        try:
            error_detail = response.json()
            print(f"Error detail: {error_detail}")
        except:
            pass