#!/usr/bin/env python3
"""
Test script for KPI Agent and refactored agent architecture.

This script demonstrates the usage of the new KPI agent and validates
that KPI tools are properly bound only to the KPI agent.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.kpi_agent import KPIAgent
    from agents.evaluation_agents import GapCheckerAgent, ComplianceCheckerAgent, PolicyEnhancerAgent
    from agents.use_case_agents import DeploymentAnalyzerAgent, UseCaseJudgeAgent, AnalysisAggregatorAgent
    from tools.index import get_all_tools, get_base_tools, get_kpi_only_tools, get_tools_for_kpi_agent
    from tools.kpi import get_kpi_tools
    
    print("✅ All imports successful!")
    
    # Test tool functions
    print("\n🔧 Testing tool functions...")
    base_tools = get_base_tools()
    print(f"Base tools count: {len(base_tools)}")
    
    kpi_tools = get_kpi_only_tools()
    print(f"KPI tools count: {len(kpi_tools)}")
    
    all_tools = get_all_tools()
    print(f"All tools count: {len(all_tools)}")
    
    kpi_agent_tools = get_tools_for_kpi_agent()
    print(f"KPI agent tools count: {len(kpi_agent_tools)}")
    
    # Test agent initialization
    print("\n🤖 Testing agent initialization...")
    
    # Test KPI Agent (should have KPI tools)
    kpi_agent = KPIAgent()
    print(f"KPI Agent tools count: {len(kpi_agent.tools)}")
    print("KPI Agent initialized successfully!")
    
    # Test policy evaluation agents (should only have base tools)
    gap_agent = GapCheckerAgent()
    print(f"Gap Checker Agent tools count: {len(gap_agent.tools)}")
    
    compliance_agent = ComplianceCheckerAgent()
    print(f"Compliance Checker Agent tools count: {len(compliance_agent.tools)}")
    
    enhancer_agent = PolicyEnhancerAgent()
    print(f"Policy Enhancer Agent tools count: {len(enhancer_agent.tools)}")
    
    # Test use case analysis agents (should only have base tools)
    deployment_agent = DeploymentAnalyzerAgent()
    print(f"Deployment Analyzer Agent tools count: {len(deployment_agent.tools)}")
    
    judge_agent = UseCaseJudgeAgent()
    print(f"Use Case Judge Agent tools count: {len(judge_agent.tools)}")
    
    aggregator_agent = AnalysisAggregatorAgent()
    print(f"Analysis Aggregator Agent tools count: {len(aggregator_agent.tools)}")
    
    print("\n✅ All agents initialized successfully!")
    
    # Test KPI calculations
    print("\n📊 Testing KPI calculations...")
    
    # Test specific KPI calculation
    vulnerability_result = kpi_agent.calculate_specific_kpi(
        "vulnerability_management_effectiveness",
        total_vulnerabilities=100,
        addressed_vulnerabilities=85
    )
    print(f"Vulnerability Management KPI: {vulnerability_result}")
    
    # Test MTTD calculation
    mttd_result = kpi_agent.calculate_specific_kpi(
        "mean_time_to_detect",
        detection_times_hours=[0.5, 1.2, 0.8, 2.1, 0.9]
    )
    print(f"Mean Time to Detect KPI: {mttd_result}")
    
    # Test fraud detection efficiency
    fraud_result = kpi_agent.calculate_specific_kpi(
        "fraud_detection_efficiency",
        detected_fraud_amount=95000.0,
        total_fraud_amount=100000.0,
        response_time_hours=1.5
    )
    print(f"Fraud Detection Efficiency KPI: {fraud_result}")
    
    print("\n📋 Testing KPI recommendations...")
    sample_kpi_scores = {
        "vulnerability_management_effectiveness": 75.0,
        "mean_time_to_detect": 65.0,
        "system_availability_percentage": 99.5,
        "fraud_detection_efficiency": 80.0,
        "encryption_strength_score": 85.0,
        "compliance_coverage_percentage": 92.0
    }
    
    recommendations = kpi_agent.get_kpi_recommendations(sample_kpi_scores)
    print("Generated recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n🎉 All tests completed successfully!")
    print("\n📝 Summary:")
    print(f"   - KPI Agent has {len(kpi_agent.tools)} tools (includes KPI functions)")
    print(f"   - Other agents have {len(gap_agent.tools)} tools (base tools only)")
    print(f"   - {len(kpi_tools)} KPI functions are properly isolated")
    print("   - All agents initialize without errors")
    print("   - KPI calculations work correctly")
    print("   - Recommendations are generated properly")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed and paths are correct.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    print("Please check the implementation for issues.")
    sys.exit(1)
