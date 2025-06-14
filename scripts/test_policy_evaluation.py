"""
Test script to demonstrate the policy evaluation system.

This script processes a sample policy document and evaluates it against standards.
"""
import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import the policy evaluation functions
from pipelines.policy_evaluation import identify_gaps, check_compliance, enhance_policy

def load_sample_policy() -> str:
    """
    Load a sample policy document for testing.
    
    Returns:
        Policy document text
    """
    # Path to a sample policy file
    policy_path = Path(project_root) / "policies" / "Access-Control-Policy.docx"
    
    # Check if the file exists
    if not policy_path.exists():
        print(f"Error: Sample policy file not found at {policy_path}")
        return "Sample policy content - Access Control Policy."
    
    # For demonstration, we'll use a simple string
    # In a real scenario, you would need to extract text from the .docx file
    return """
    Policy #: x.xxx
    Title: Access Control Policy
    Effective Date: MM/DD/YY
    
    PURPOSE
    To ensure that access controls are implemented and in compliance with IT security policies, standards, and procedures.
    
    REFERENCE
    National Institute of Standards and Technology (NIST) Special Publications (SP): 
    NIST SP 800-53a –Access Control (AC), NIST SP 800-12, NIST 800-46, NIST SP 800-48, 
    NIST SP 800-77, NIST SP 800-94, NIST SP 800-97, NIST SP 800-100, NIST SP 800-113, 
    NIST SP 800-114, NIST SP 800-121, NIST SP 800-124, NIST SP 800-164;
    NIST Federal Information Processing Standards(FIPS) 199
    
    POLICY
    This policy is applicable to all departments and users of cisecurity resources and assets.
    
    1. ACCOUNT MANAGEMENT
    IT Department shall:
    a. Identify and select the following types of information system accounts to support 
       organizational missions and business functions: individual, shared, group, system, 
       guest/anonymous, emergency, developer/manufacturer/vendor, temporary, and service.
    b. Assign account managers for information system accounts.
    c. Establish conditions for group and role membership.
    d. Specify authorized users of the information system, group and role membership, 
       and access authorizations (i.e., privileges) and other attributes (as required) for each account.
    e. Require approvalsby system owners for requests to create information system accounts.
    f. Create, enable, modify, disable, and remove information system accounts in accordance with approved procedures.
    g. Monitor the use of information system accounts.
    """

def load_sample_standards() -> List[str]:
    """
    Load sample standards for testing.
    
    Returns:
        List of standard document texts
    """
    # For demonstration, we'll use simple strings
    # In a real scenario, you would load these from files
    return [
        """
        PCI DSS Requirements and Testing Procedures:
        
        Requirement 7: Restrict Access to System Components and Cardholder Data by Business Need to Know
        
        7.1 Limit access to system components and cardholder data to only those individuals whose jobs require such access.
        
        7.1.1 Define and document access needs and privilege assignments for all user roles.
        
        7.1.2 Restrict access to privileged user IDs to least privileges necessary to perform job responsibilities.
        
        7.1.3 Assign access based on individual personnel's job classification and function.
        
        7.1.4 Implement an access control system(s) for systems components with multiple users to restrict access based on a user's need to know, and that is set to "deny all" unless specifically allowed.
        
        7.2 Implement system security features to ensure proper user authentication and access management for all system components.
        
        7.2.1 Cover all system components.
        
        7.2.2 Assign privileges to individuals based on job classification and function.
        
        7.2.3 Implement a default "deny-all" setting.
        """,
        
        """
        NIST SP 800-53 Access Control Guidelines:
        
        AC-2 Account Management
        
        The organization:
        
        a. Identifies and selects the following types of information system accounts to support organizational missions/business functions: [Assignment: organization-defined information system account types];
        
        b. Assigns account managers for information system accounts;
        
        c. Establishes conditions for group and role membership;
        
        d. Specifies authorized users of the information system, group and role membership, and access authorizations (i.e., privileges) and other attributes (as required) for each account;
        
        e. Requires approvals by [Assignment: organization-defined personnel or roles] for requests to create information system accounts;
        
        f. Creates, enables, modifies, disables, and removes information system accounts in accordance with [Assignment: organization-defined procedures or conditions];
        
        g. Monitors the use of information system accounts;
        
        h. Notifies account managers:
           1. When accounts are no longer required;
           2. When users are terminated or transferred; and
           3. When individual information system usage or need-to-know changes;
        
        i. Authorizes access to the information system based on:
           1. A valid access authorization;
           2. Intended system usage; and
           3. Other attributes as required by the organization or associated missions/business functions;
        
        j. Reviews accounts for compliance with account management requirements [Assignment: organization-defined frequency]; and
        
        k. Establishes a process for reissuing shared/group account credentials (if deployed) when individuals are removed from the group.
        """
    ]

def run_test():
    """Run a test of the policy evaluation pipeline."""
    print("Loading sample policy and standards...")
    policy = load_sample_policy()
    standards = load_sample_standards()
    
    print("\n===== GAP IDENTIFICATION =====")
    print("Running gap identification...")
    gap_results = identify_gaps(policy, standards)
    print(json.dumps(gap_results[0], indent=2))  # Show the first chunk only for brevity
    
    print("\n===== COMPLIANCE CHECK =====")
    print("Running compliance check...")
    compliance_results = check_compliance(policy, standards)
    print(json.dumps(compliance_results[0], indent=2))  # Show the first chunk only for brevity
    
    print("\n===== POLICY ENHANCEMENT =====")
    print("Running policy enhancement...")
    enhancement_results = enhance_policy(policy, standards)
    print(json.dumps(enhancement_results[0], indent=2))  # Show the first chunk only for brevity
    
    print("\nTest complete!")

if __name__ == "__main__":
    run_test()
