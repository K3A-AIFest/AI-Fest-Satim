"""
Script to test the use case processor functionality.
"""
import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from pipelines.use_case_processor import process_use_case

def main():
    """Run a test of the use case processor."""
    print("Testing Use Case Processor...")
    
    # Sample use case text
    use_case = """
    Security Use Case: Multi-Factor Authentication Implementation
    
    Description:
    This use case details the implementation of Multi-Factor Authentication (MFA) across all corporate systems to enhance security posture and reduce unauthorized access risks.
    
    Objectives:
    1. Implement MFA for all user accounts across critical systems
    2. Reduce unauthorized access incidents by 80%
    3. Ensure compliance with PCI-DSS and internal security policies
    
    Implementation Details:
    - Deploy MFA solution that supports multiple authentication methods (SMS, app-based tokens, hardware tokens)
    - Integrate with current identity management system
    - Implement risk-based authentication for sensitive operations
    - Create user training materials for new authentication procedures
    - Establish monitoring for failed authentication attempts
    
    Success Metrics:
    - 100% of critical systems protected by MFA within 3 months
    - Reduction in successful phishing attacks by 70%
    - User adoption rate of 95% within 6 months
    
    Timeline:
    - Phase 1 (Month 1-2): Implementation for admin accounts
    - Phase 2 (Month 2-4): Implementation for all employee accounts
    - Phase 3 (Month 4-6): Implementation for external partners
    
    Resources:
    - Identity management team (2 FTE)
    - Security engineering (1 FTE)
    - Help desk support for user training (temporary)
    - Estimated budget: $150,000
    """
    
    # Sample standards for testing
    standards = [
        """
        PCI DSS Requirement 8.2.1: 
        Use strong authentication methods for all users accessing cardholder data environment.
        Implement multi-factor authentication for all personnel with non-console administrative access.
        """,
        """
        PCI DSS Requirement 8.2.3:
        Incorporate multi-factor authentication for all remote network access that originates from outside the entity's network.
        """
    ]
    
    # Sample policies for testing
    policies = [
        """
        Corporate Authentication Policy:
        All access to corporate systems must be protected by multi-factor authentication.
        Authentication systems must support at least two of the following:
        - Something you know (password, PIN)
        - Something you have (hardware token, smart card)
        - Something you are (biometric)
        """
    ]
    
    # Process the use case
    result = process_use_case(use_case, standards, policies)
    
    # Save the full result to a JSON file for detailed review first
    output_file = project_root / "use_case_processor_test_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nFull results saved to: {output_file}")
    
    # Check what we got back
    print("\n===== RESULT STRUCTURE =====")
    print(f"Result type: {type(result)}")
    print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    
    # Display the results if available
    print("\n===== USE CASE PROCESSOR RESULTS =====")
    if isinstance(result, dict) and 'aggregated_analysis' in result and result['aggregated_analysis']:
        print(f"Overall Score: {result['aggregated_analysis']['overall_score']}")
        print(f"Overall Assessment: {result['aggregated_analysis']['overall_assessment']}")
        
        print("\n--- Key Findings ---")
        for i, finding in enumerate(result['aggregated_analysis']['key_findings'], 1):
            print(f"{i}. {finding}")
        
        print("\n--- Recommended Next Steps ---")
        for i, step in enumerate(result['aggregated_analysis']['recommended_next_steps'], 1):
            print(f"{i}. {step}")
    else:
        print("aggregated_analysis not available or is None")
        print("Available data:")
        for key, value in result.items():
            print(f"  {key}: {type(value)}")

if __name__ == "__main__":
    main()
