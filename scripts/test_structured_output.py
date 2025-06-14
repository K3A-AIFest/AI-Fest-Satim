#!/usr/bin/env python3
"""
Test script to verify the structured output from the policy evaluation pipeline.

This script loads a sample policy and standard, runs all three evaluations,
and prints out the structured results to verify they match the expected format.
"""
import sys
import os
import json
from pathlib import Path
import logging

# Set up path to import from parent directory
sys.path.append(str(Path(__file__).parent.parent))

# Import evaluation functions
from pipelines.policy_evaluation import identify_gaps, check_compliance, enhance_policy

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_sample_files():
    """Load a sample policy and standard for testing."""
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Load a sample policy file
    policy_path = root_dir / "policies" / "Access-Control-Policy.docx"
    if not policy_path.exists():
        policy_path = root_dir / "policies" / "Information-Security-Policy.docx"
    
    if not policy_path.exists():
        logger.error("Could not find a sample policy file.")
        return None, None
    
    # Load a sample standard file
    standard_path = root_dir / "standards" / "PCI-DSS-v4_0_1.pdf"
    if not standard_path.exists():
        standard_path = next(root_dir.glob("standards/*.pdf"), None)
    
    if not standard_path:
        logger.error("Could not find a sample standard file.")
        return None, None
    
    # Read the files (assuming they're text files for this test)
    try:
        # For simplicity in this test, use simple extracts instead of parsing docx/pdf
        policy_content = "This is a sample policy for testing purposes. It covers access control."
        standard_content = ["This is a sample standard for testing. It requires strong access controls."]
        
        logger.info(f"Loaded sample policy and standard for testing.")
        return policy_content, standard_content
    except Exception as e:
        logger.error(f"Error loading files: {e}")
        return None, None

def test_gap_analysis(policy, standards):
    """Test the gap analysis function and print results."""
    logger.info("Testing gap analysis...")
    try:
        results = identify_gaps(policy, standards)
        print("\n=== GAP ANALYSIS RESULTS ===")
        for i, result in enumerate(results):
            print(f"\nChunk {i+1} Analysis:")
            print(f"Classification: {result['classification']}")
            print(f"Original Content: {result['original_content'][:50]}...")
            print(f"Gaps Identified: {result['gaps']}")
            print(f"Rationale: {result['rationale'][:100]}...")
            print(f"References: {result['references']}")
        return True
    except Exception as e:
        logger.error(f"Error in gap analysis test: {e}")
        return False

def test_compliance_check(policy, standards):
    """Test the compliance check function and print results."""
    logger.info("Testing compliance check...")
    try:
        results = check_compliance(policy, standards)
        print("\n=== COMPLIANCE CHECK RESULTS ===")
        for i, result in enumerate(results):
            print(f"\nChunk {i+1} Compliance:")
            print(f"Classification: {result['classification']}")
            print(f"Original Content: {result['original_content'][:50]}...")
            print(f"Issues: {result['issues']}")
            print(f"Rationale: {result['rationale'][:100]}...")
            print(f"References: {result['references']}")
        return True
    except Exception as e:
        logger.error(f"Error in compliance check test: {e}")
        return False

def test_policy_enhancement(policy, standards):
    """Test the policy enhancement function and print results."""
    logger.info("Testing policy enhancement...")
    try:
        results = enhance_policy(policy, standards)
        print("\n=== POLICY ENHANCEMENT RESULTS ===")
        for i, result in enumerate(results):
            print(f"\nChunk {i+1} Enhancement:")
            print(f"Classification: {result['classification']}")
            print(f"Original Content: {result['original_content'][:50]}...")
            print(f"Enhanced Version: {result['enhanced_version'][:50]}...")
            print(f"Changes: {result['changes']}")
            print(f"Rationale: {result['rationale'][:100]}...")
        return True
    except Exception as e:
        logger.error(f"Error in policy enhancement test: {e}")
        return False

def main():
    """Run tests to verify structured output."""
    logger.info("Starting structured output test")
    
    # Load sample files
    policy, standards = load_sample_files()
    if not policy or not standards:
        logger.error("Could not load test files. Exiting.")
        sys.exit(1)
    
    # Run tests
    gap_success = test_gap_analysis(policy, standards)
    compliance_success = test_compliance_check(policy, standards)
    enhancement_success = test_policy_enhancement(policy, standards)
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    print(f"Gap Analysis: {'PASS' if gap_success else 'FAIL'}")
    print(f"Compliance Check: {'PASS' if compliance_success else 'FAIL'}")
    print(f"Policy Enhancement: {'PASS' if enhancement_success else 'FAIL'}")
    
    # Exit with status code
    if gap_success and compliance_success and enhancement_success:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
