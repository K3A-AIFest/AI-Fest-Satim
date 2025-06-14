"""
Script to test the KPI agent functionality specifically.
"""
import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.kpi_agent import KPIAgent

def main():
    """Run tests of the KPI agent."""
    print("Testing KPI Agent...")
    
    # Initialize the KPI agent
    kpi_agent = KPIAgent()
    
    # Sample use case text (same as in the use case processor test)
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
   
    print("\n===== TESTING KPI AGENT =====")
    
    try:
        # Test the KPI analysis
        print("Calling analyze_security_kpis...")
        result = kpi_agent.analyze_security_kpis(
            use_case=use_case,
            standards=standards,
            policies=policies
        )
        
        print("\n--- KPI Analysis Results ---")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"Result keys: {list(result.keys())}")
            
            # Print KPI scores if available
            if 'kpi_scores' in result:
                print(f"\nKPI Scores ({len(result['kpi_scores'])} metrics):")
                for kpi, score in result['kpi_scores'].items():
                    print(f"  {kpi}: {score}")
            
            # Print overall assessment
            if 'overall_score' in result:
                print(f"\nOverall Score: {result['overall_score']}")
            
            if 'risk_level' in result:
                print(f"Risk Level: {result['risk_level']}")
            
            # Print recommendations
            if 'recommendations' in result:
                print(f"\nRecommendations ({len(result['recommendations'])}):")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"  {i}. {rec}")
        else:
            print(f"Unexpected result type: {type(result)}")
            print(f"Result content: {result}")
        
        # Save the result
        output_file = project_root / "kpi_agent_test_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nFull results saved to: {output_file}")
        
    except Exception as e:
        print(f"\nERROR during KPI analysis: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print("Traceback:")
        traceback.print_exc()
    
    print("\n===== TESTING INDIVIDUAL KPI CALCULATIONS =====")
    
    # Test individual KPI calculations
    individual_kpis = [
        "vulnerability_management_effectiveness",
        "mean_time_to_detect", 
        "mean_time_to_respond",
        "security_coverage_score",
        "system_availability_percentage"
    ]
    
    for kpi_name in individual_kpis:
        try:
            print(f"\nTesting {kpi_name}...")
            result = kpi_agent.calculate_specific_kpi(
                kpi_name=kpi_name,
                
            )
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    main()
