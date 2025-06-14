#!/usr/bin/env python3
"""
Test script to evaluate a small policy chunk against one standard using the policy evaluation API.
This script tests only the evaluate-policy endpoint with minimal test data.
"""
import requests
import json
from pprint import pprint

# API base URL - adjust if your server runs on a different port or host
API_BASE_URL = "http://localhost:8000"

def test_simple_evaluation():
    """
    Test the policy evaluation endpoint with a small policy chunk and one standard.
    """
    print("\n===== SIMPLE POLICY EVALUATION TEST =====")
    
    # The endpoint we want to test
    url = f"{API_BASE_URL}/api/v1/evaluate-policy"
    
    # A small policy chunk for testing
    policy_chunk = """
    # Access Control Policy
    
    All users must authenticate using multi-factor authentication (MFA) before accessing 
    sensitive systems. Access rights must be reviewed quarterly and immediately revoked 
    upon termination of employment. System owners are responsible for approving access 
    requests for their systems.
    """
    
    # A single standard to evaluate against
    standard = """
    NIST SP 800-53 Access Control Guidelines:
    
    AC-2 Account Management
    
    The organization:
    
    a. Identifies and selects the following types of information system accounts to support organizational missions/business functions;
    
    b. Assigns account managers for information system accounts;
    
    c. Establishes conditions for group and role membership;
    
    d. Specifies authorized users of the information system, group and role membership, and access authorizations;
    
    e. Requires approvals by system owners for requests to create information system accounts;
    
    f. Creates, enables, modifies, disables, and removes information system accounts in accordance with approved procedures;
    
    g. Monitors the use of information system accounts;
    
    h. Notifies account managers when accounts are no longer required, when users are terminated or transferred, and when system usage or need-to-know changes;
    
    i. Authorizes access to the information system based on a valid access authorization, intended system usage, and other attributes as required;
    
    j. Reviews accounts for compliance with account management requirements periodically; and
    
    k. Establishes a process for reissuing shared/group account credentials when individuals are removed from the group.
    """
    
    # Prepare request data
    data = {
        "policy": policy_chunk,
        "standards": [standard]  # List with just one standard
    }
    
    try:
        # Send request to the API
        print("Sending request to policy evaluation endpoint...")
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        # Process response
        print(f"Status code: {response.status_code}")
        result = response.json()
        
        # Print summary of results
        print("\nResults summary:")
        if "results" in result and result["results"]:
            chunk_result = result["results"][0]  # Should only have one chunk
            
            print("\n--- Gap Analysis ---")
            print(f"Classification: {chunk_result['gap_analysis']['classification']}")
            print(f"Number of gaps identified: {len(chunk_result['gap_analysis']['gaps'])}")
            if chunk_result['gap_analysis']['gaps']:
                print("First gap identified:", chunk_result['gap_analysis']['gaps'][0])
                
            print("\n--- Compliance Assessment ---")
            print(f"Classification: {chunk_result['compliance_assessment']['classification']}")
            print(f"Number of compliance issues: {len(chunk_result['compliance_assessment']['issues'])}")
            if chunk_result['compliance_assessment']['issues']:
                print("First compliance issue:", chunk_result['compliance_assessment']['issues'][0])
                
            print("\n--- Enhancement Suggestions ---")
            print(f"Classification: {chunk_result['enhancement']['classification']}")
            print(f"Number of changes: {len(chunk_result['enhancement']['changes'])}")
            if chunk_result['enhancement']['changes']:
                print("First suggested change:", chunk_result['enhancement']['changes'][0])
            
            # Save full results to file
            with open("simple_evaluation_result.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\nFull results saved to simple_evaluation_result.json")
        else:
            print("No results returned.")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return False

if __name__ == "__main__":
    # Run the test
    test_simple_evaluation()