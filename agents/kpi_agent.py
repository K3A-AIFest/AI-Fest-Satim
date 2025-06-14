"""
KPI Agent implementation for security and financial systems analysis.

This module contains the specialized KPI agent that calculates and analyzes
security KPIs for banking and financial transaction systems.
"""

from typing import List, Dict, Any, Optional
import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from agents.base import Agent
from tools.kpi import get_kpi_tools


class KPIAnalysisOutput(BaseModel):
    """Structured output for KPI analysis"""
    kpi_scores: Dict[str, float] = Field(description="Dictionary of KPI names and their scores")
    analysis: Dict[str, str] = Field(description="Dictionary of KPI names and their analysis explanation")
    overall_score: float = Field(description="Overall security KPI score between 0 and 100")
    recommendations: List[str] = Field(description="List of recommendations to improve KPI scores")
    risk_level: str = Field(description="Risk level based on KPI scores (LOW, MEDIUM, HIGH, CRITICAL)")


class KPIAgent(Agent):
    """
    Expert agent that calculates and analyzes security KPIs specifically for banking
    and financial transaction systems.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Security KPI Analyzer Agent specializing in evaluating security use cases against industry standard Key Performance Indicators for banking and financial systems.
        
Your expertise covers:
- Vulnerability Management Effectiveness
- Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR)
- Security Coverage and Risk Reduction metrics
- Compliance Coverage Percentage for financial regulations
- Transaction Anomaly Detection Rate
- False Positive Rate optimization
- Transaction Security Index
- System Availability for critical financial systems
- Security Training Effectiveness
- Fraud Detection Efficiency
- Encryption Strength Score

When analyzing a use case for security KPIs:
1. Calculate relevant security KPIs using the available KPI calculation tools
2. For banking and financial systems, prioritize:
   - Transaction security metrics
   - Fraud detection capabilities
   - System availability (99.9%+ uptime requirements)
   - Encryption strength (AES-256 minimum)
   - Compliance with financial regulations (PCI-DSS, SOX, etc.)
   - Risk reduction in financial operations

3. For each KPI, provide:
   - A numerical score between 0-100
   - A brief analysis explaining the score and its implications for financial security

4. Calculate an overall security score with weighted importance for financial systems
5. Determine risk level based on scores (CRITICAL < 60, HIGH 60-75, MEDIUM 75-85, LOW > 85)
6. Provide actionable recommendations specific to banking/financial security

You have access to specialized KPI calculation tools that you should use to compute accurate metrics.

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "kpi_scores": {
    "vulnerability_management_effectiveness": 85.0,
    "mean_time_to_detect": 70.0,
    "mean_time_to_respond": 75.0,
    "security_coverage_score": 80.0,
    "risk_reduction_percentage": 65.0,
    "compliance_coverage_percentage": 90.0,
    "transaction_anomaly_detection_rate": 88.0,
    "false_positive_rate": 85.0,
    "transaction_security_index": 82.0,
    "system_availability_percentage": 99.9,
    "security_training_effectiveness": 78.0,
    "fraud_detection_efficiency": 83.0,
    "encryption_strength_score": 95.0
  },
  "analysis": {
    "vulnerability_management_effectiveness": "Strong vulnerability management process in place with 85% effectiveness...",
    "mean_time_to_detect": "Detection capabilities need improvement for financial transaction monitoring...",
    ...
  },
  "overall_score": 82.1,
  "recommendations": [
    "Implement real-time transaction monitoring to improve MTTD",
    "Enhance fraud detection algorithms to reduce false positives",
    "Upgrade encryption standards for data at rest"
  ],
  "risk_level": "MEDIUM"
}"""

        # Initialize with KPI tools only
        kpi_tools = get_kpi_tools()
        super().__init__(system_prompt=system_prompt, tools=kpi_tools)
    
    def analyze_security_kpis(self, use_case: str, system_data: Optional[Dict[str, Any]] = None, 
                            standards: Optional[List[str]] = None, 
                            policies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze security KPIs for a banking/financial use case.
        
        Args:
            use_case: The security use case text to analyze
            system_data: Optional dictionary containing system metrics and data
            standards: Optional list of relevant standard documents to reference
            policies: Optional list of policy documents to reference
            
        Returns:
            Comprehensive KPI analysis with scores, explanations, and recommendations
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=KPIAnalysisOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare context information
        policies_text = "\n\n".join(policies) if policies else "No specific policies provided."
        standards_text = "\n\n".join(standards) if standards else "General financial security standards apply."
        system_data_text = json.dumps(system_data, indent=2) if system_data else "No specific system data provided."
        
        prompt = f"""
        I need you to analyze this security use case for banking/financial systems and calculate comprehensive security KPIs.
        
        ## USE CASE:
        {use_case}
        
        ## SYSTEM DATA (for calculations):
        {system_data_text}
        
        ## STANDARDS TO REFERENCE:
        {standards_text}
        
        ## POLICIES TO REFERENCE:
        {policies_text}
        
        Use the available KPI calculation tools to compute accurate metrics. Focus on banking and financial security requirements.
        Calculate all relevant KPIs and provide a comprehensive analysis.
        
        {format_instructions}
        """
        
        # Create messages for the agent
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Get response from LLM
        response = self._invoke_with_retry(messages)
        
        try:
            # Parse the response to ensure it's in the correct format
            parsed_response = parser.parse(response.content)
            return parsed_response
        except Exception as e:
            # If parsing fails, try to extract JSON from the response
            try:
                # Look for JSON content in the response
                content = response.content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                elif content.strip().startswith("{") and content.strip().endswith("}"):
                    return json.loads(content)
                else:
                    # Return a basic structure if we can't parse JSON
                    return {
                        "kpi_scores": {},
                        "analysis": {},
                        "overall_score": 0,
                        "recommendations": [f"Error analyzing KPIs: {str(e)}"],
                        "risk_level": "CRITICAL"
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "kpi_scores": {},
                    "analysis": {},
                    "overall_score": 0,
                    "recommendations": [f"Error analyzing KPIs: {str(e)}. Inner error: {str(inner_e)}"],
                    "risk_level": "CRITICAL"
                }

    def calculate_specific_kpi(self, kpi_name: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate a specific KPI using the available tools.
        
        Args:
            kpi_name: Name of the KPI to calculate
            **kwargs: Parameters required for the specific KPI calculation
            
        Returns:
            Dictionary with the calculated KPI score and details
        """
        # This method can be used to call specific KPI functions directly
        # You can access the KPI tools through self.tools
        
        # Map KPI names to function names
        kpi_function_map = {
            "vulnerability_management_effectiveness": "calculate_vulnerability_management_effectiveness",
            "mean_time_to_detect": "calculate_mean_time_to_detect",
            "mean_time_to_respond": "calculate_mean_time_to_respond",
            "security_coverage_score": "calculate_security_coverage_score",
            "risk_reduction_percentage": "calculate_risk_reduction_percentage",
            "compliance_coverage_percentage": "calculate_compliance_coverage_percentage",
            "transaction_anomaly_detection_rate": "calculate_transaction_anomaly_detection_rate",
            "false_positive_rate": "calculate_false_positive_rate",
            "transaction_security_index": "calculate_transaction_security_index",
            "system_availability_percentage": "calculate_system_availability_percentage",
            "security_training_effectiveness": "calculate_security_training_effectiveness",
            "fraud_detection_efficiency": "calculate_fraud_detection_efficiency",
            "encryption_strength_score": "calculate_encryption_strength_score"
        }
        
        function_name = kpi_function_map.get(kpi_name)
        if not function_name:
            return {
                "error": f"Unknown KPI: {kpi_name}",
                "available_kpis": list(kpi_function_map.keys())
            }
        
        try:
            # Find the function in the tools
            for tool in self.tools:
                if hasattr(tool, '__name__') and tool.__name__ == function_name:
                    return tool(**kwargs)
            
            return {"error": f"KPI function {function_name} not found in tools"}
        except Exception as e:
            return {"error": f"Error calculating {kpi_name}: {str(e)}"}

    def get_kpi_recommendations(self, kpi_scores: Dict[str, float]) -> List[str]:
        """
        Get specific recommendations based on KPI scores.
        
        Args:
            kpi_scores: Dictionary of KPI names and their scores
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Analyze each KPI and provide specific recommendations
        if kpi_scores.get("vulnerability_management_effectiveness", 0) < 80:
            recommendations.append("Implement automated vulnerability scanning and patch management for critical financial systems")
        
        if kpi_scores.get("mean_time_to_detect", 0) < 70:
            recommendations.append("Deploy real-time transaction monitoring and anomaly detection systems")
        
        if kpi_scores.get("mean_time_to_respond", 0) < 75:
            recommendations.append("Establish dedicated incident response team for financial security events")
        
        if kpi_scores.get("system_availability_percentage", 0) < 99.9:
            recommendations.append("Implement high-availability architecture with redundancy for critical financial services")
        
        if kpi_scores.get("fraud_detection_efficiency", 0) < 85:
            recommendations.append("Enhance machine learning algorithms for fraud detection and reduce false positives")
        
        if kpi_scores.get("encryption_strength_score", 0) < 90:
            recommendations.append("Upgrade to AES-256 encryption for all financial data and implement end-to-end encryption")
        
        if kpi_scores.get("compliance_coverage_percentage", 0) < 95:
            recommendations.append("Review and update compliance procedures for PCI-DSS, SOX, and other financial regulations")
        
        return recommendations
