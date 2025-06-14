"""
Test script to send requests to the Policy Evaluation API endpoints.

This script interacts with all API endpoints to test functionality with sample data.
"""
import os
import json
import sys
import requests
from pathlib import Path
from typing import List, Dict, Any
from pprint import pprint

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import the sample data loader functions
from scripts.test_policy_evaluation import load_sample_policy, load_sample_standards

# API base URL
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("\n===== TESTING HEALTH CHECK ENDPOINT =====")
    
    url = f"{API_BASE_URL}/health"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print("Response:")
        pprint(response.json())
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

def test_gap_identification():
    """Test the gap identification endpoint."""
    print("\n===== TESTING GAP IDENTIFICATION ENDPOINT =====")
    
    url = f"{API_BASE_URL}/api/v1/identify-gaps"
    
    # Prepare request data
    data = {
        "policy": load_sample_policy(),
        "standards": load_sample_standards()
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print("Response (first gap):")
        result = response.json()
        if result["results"] and len(result["results"]) > 0:
            pprint(result["results"][0])
        else:
            print("No gaps identified.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return False

def test_compliance_check():
    """Test the compliance check endpoint."""
    print("\n===== TESTING COMPLIANCE CHECK ENDPOINT =====")
    
    url = f"{API_BASE_URL}/api/v1/check-compliance"
    
    # Prepare request data
    data = {
        "policy": load_sample_policy(),
        "standards": load_sample_standards()
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print("Response (first compliance check):")
        result = response.json()
        if result["results"] and len(result["results"]) > 0:
            pprint(result["results"][0])
        else:
            print("No compliance issues found.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return False

def test_policy_enhancement():
    """Test the policy enhancement endpoint."""
    print("\n===== TESTING POLICY ENHANCEMENT ENDPOINT =====")
    
    url = f"{API_BASE_URL}/api/v1/enhance-policy"
    
    # Prepare request data
    data = {
        "policy": load_sample_policy(),
        "standards": load_sample_standards()
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print("Response (first enhancement suggestion):")
        result = response.json()
        if result["results"] and len(result["results"]) > 0:
            pprint(result["results"][0])
        else:
            print("No enhancement suggestions found.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return False

def test_comprehensive_evaluation():
    """Test the comprehensive evaluation endpoint."""
    print("\n===== TESTING COMPREHENSIVE EVALUATION ENDPOINT =====")
    
    url = f"{API_BASE_URL}/api/v1/evaluate-policy"
    
    # Prepare request data
    data = {
        "policy": load_sample_policy(),
        "standards": load_sample_standards()
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print("Response (summary):")
        result = response.json()
        
        print("Gap analysis (count):", len(result.get("gaps", [])))
        print("Compliance checks (count):", len(result.get("compliance", [])))
        print("Enhancement suggestions (count):", len(result.get("enhancements", [])))
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return False

def run_all_tests():
    """Run all API tests."""
    print("Starting API tests...\n")
    
    # Check if server is running
    if not test_health_check():
        print("\nError: Server may not be running. Please start the server first.")
        return
    
    # Run all endpoint tests
    test_gap_identification()
    test_compliance_check()
    test_policy_enhancement()
    test_comprehensive_evaluation()
    
    print("\nAll tests completed!")

def run_real_policy_test():
    """Test with a real policy document from the policies folder."""
    from embed.document_loader import DocumentLoader
    
    print("\n===== TESTING WITH REAL POLICY DOCUMENT =====")
    
    # Load a real policy document
    policy_path = Path(project_root) / "policies"
    loader = DocumentLoader()
    
    try:
        # List available policies
        print("Available policies:")
        for i, policy_file in enumerate(policy_path.glob("*.docx")):
            print(f"{i+1}. {policy_file.name}")
        
        # For this test, use the Information Security Policy
        target_policy = "Information-Security-Policy.docx"
        policy_file_path = policy_path / target_policy
        
        if not policy_file_path.exists():
            print(f"Policy file not found: {policy_file_path}")
            return
        
        # Using the test sample standards for simplicity
        standards = load_sample_standards()
        
        # Load policy content (this is a simplified approach)
        import docx
        doc = docx.Document(policy_file_path)
        policy_content = "\n".join([para.text for para in doc.paragraphs])
        
        # Call the comprehensive evaluation endpoint
        url = f"{API_BASE_URL}/api/v1/evaluate-policy"
        
        data = {
            "policy": policy_content,
            "standards": standards
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\nTested policy: {target_policy}")
        print("Results summary:")
        print("Gap analysis (count):", len(result.get("gaps", [])))
        print("Compliance checks (count):", len(result.get("compliance", [])))
        print("Enhancement suggestions (count):", len(result.get("enhancements", [])))
        
        # Save the results to a file
        output_file = Path(project_root) / "scripts" / f"{target_policy.split('.')[0]}_evaluation.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Full results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error testing with real policy: {e}")

if __name__ == "__main__":
    # Regular API tests
    run_all_tests()
    
    # Test with real policy document
    try:
        import docx
        run_real_policy_test()
    except ImportError:
        print("\nTo test with real policy documents, install python-docx:")
        print("pip install python-docx")
