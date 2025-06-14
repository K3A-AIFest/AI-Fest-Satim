"""
KPI Agent implementation for security and financial systems analysis.

This module contains the specialized KPI agent that calculates and analyzes
security KPIs for banking and financial transaction systems.
"""

from typing import List, Dict, Any, Optional
import json
import re
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
7. Make sure to rename system variables to match the tool function parameters signature.

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
    
    def analyze_security_kpis(self, use_case: str, 
                            standards: Optional[List[str]] = None, 
                            policies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze security KPIs for a banking/financial use case.
        
        Args:
            use_case: The security use case text to analyze
            standards: Optional list of relevant standard documents to reference
            policies: Optional list of policy documents to reference
            
        Returns:
            Comprehensive KPI analysis with scores, explanations, and recommendations
        """
        try:
            # Step 1: Extract metrics from the use case text
            extracted_metrics = self._extract_kpi_metrics_from_text(use_case)
            
            # Step 2: Calculate KPIs using extracted metrics
            kpi_scores, analysis = self._calculate_kpis_with_extracted_metrics(extracted_metrics)
            
            # Step 3: Calculate overall score
            if kpi_scores:
                overall_score = sum(kpi_scores.values()) / len(kpi_scores)
            else:
                overall_score = 0.0
            
            # Step 4: Determine risk level
            if overall_score < 60:
                risk_level = "CRITICAL"
            elif overall_score < 75:
                risk_level = "HIGH"
            elif overall_score < 85:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Step 5: Generate recommendations
            recommendations = self.get_kpi_recommendations(kpi_scores)
            
            # Add context-specific recommendations based on use case content
            if "mfa" in use_case.lower() or "authentication" in use_case.lower():
                recommendations.append("Continue monitoring MFA adoption rates and user satisfaction")
                if overall_score < 80:
                    recommendations.append("Consider implementing adaptive authentication based on risk scoring")
            
            if "phishing" in use_case.lower():
                recommendations.append("Implement advanced email security and user awareness training")
            
            # Prepare context information for additional analysis
            policies_text = "\n\n".join(policies) if policies else "No specific policies provided."
            standards_text = "\n\n".join(standards) if standards else "General financial security standards apply."
            
            # Add compliance-specific recommendations
            if "pci" in standards_text.lower():
                recommendations.append("Ensure all KPI improvements align with PCI-DSS requirements")
            
            return {
                "kpi_scores": kpi_scores,
                "analysis": analysis,
                "overall_score": round(overall_score, 2),
                "recommendations": recommendations,
                "risk_level": risk_level
            }
            
        except Exception as e:
            # Fallback error handling
            return {
                "kpi_scores": {},
                "analysis": {},
                "overall_score": 0,
                "recommendations": [f"Error analyzing KPIs: {str(e)}"],
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
    
    def _extract_kpi_metrics_from_text(self, use_case: str) -> Dict[str, Any]:
        """
        Extract or estimate KPI metrics from use case text.
        
        Args:
            use_case: The use case text to analyze
            
        Returns:
            Dictionary of extracted/estimated metrics for KPI calculations
        """
        metrics = {}
        
        # Look for percentages and numbers in the text
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        
        percentages = re.findall(percentage_pattern, use_case)
        numbers = re.findall(number_pattern, use_case)
        
        # Convert to floats
        percentages = [float(p) for p in percentages]
        numbers = [float(n) for n in numbers]
        
        # Vulnerability Management Effectiveness
        if "vulnerability" in use_case.lower() or "patch" in use_case.lower():
            # Look for vulnerability-related metrics
            if percentages:
                # Use highest percentage as effectiveness rate
                effectiveness_rate = max(percentages)
                total_vulns = 100 if not numbers else int(max(numbers))
                addressed_vulns = int((effectiveness_rate / 100) * total_vulns)
                metrics["vulnerability_management"] = {
                    "total_vulnerabilities": total_vulns,
                    "addressed_vulnerabilities": addressed_vulns
                }
            else:
                # Default values for typical enterprise
                metrics["vulnerability_management"] = {
                    "total_vulnerabilities": 50,
                    "addressed_vulnerabilities": 42  # 84% typical rate
                }
        
        # Mean Time to Detect/Respond
        if "detect" in use_case.lower() or "incident" in use_case.lower() or "response" in use_case.lower():
            # Look for time-related metrics
            detection_times = [2.5, 4.0, 1.5, 3.2, 2.8]  # Default sample times in hours
            response_times = [4.0, 6.5, 3.0, 5.2, 4.8]   # Default sample times in hours
            
            metrics["mean_time_to_detect"] = {
                "detection_times_hours": detection_times
            }
            metrics["mean_time_to_respond"] = {
                "response_times_hours": response_times
            }
        
        # Security Coverage Score
        if "implement" in use_case.lower() or "coverage" in use_case.lower():
            # Estimate coverage based on implementation scope
            coverage_areas = {}
            if "mfa" in use_case.lower() or "authentication" in use_case.lower():
                coverage_areas["authentication"] = {"score": 85.0, "implemented": True}
            if "encrypt" in use_case.lower():
                coverage_areas["encryption"] = {"score": 90.0, "implemented": True}
            if "monitor" in use_case.lower():
                coverage_areas["monitoring"] = {"score": 75.0, "implemented": True}
            if "access" in use_case.lower() or "authorization" in use_case.lower():
                coverage_areas["access_control"] = {"score": 80.0, "implemented": True}
            
            if not coverage_areas:
                # Default coverage areas
                coverage_areas = {
                    "general_security": {"score": 70.0, "implemented": True}
                }
            
            metrics["security_coverage"] = {
                "coverage_metrics": coverage_areas
            }
        
        # Risk Reduction
        if "risk" in use_case.lower() or "reduce" in use_case.lower():
            # Extract risk reduction percentages
            if percentages:
                reduction_pct = max([p for p in percentages if p <= 100])
                initial_risk = 85.0  # Typical initial risk level
                residual_risk = initial_risk * (100 - reduction_pct) / 100
            else:
                initial_risk = 85.0
                residual_risk = 25.0  # Assume good risk reduction
            
            metrics["risk_reduction"] = {
                "initial_risk_level": initial_risk,
                "residual_risk_level": residual_risk
            }
        
        # Compliance Coverage
        if "compliance" in use_case.lower() or "pci" in use_case.lower() or "policy" in use_case.lower():
            # Extract compliance metrics
            if percentages:
                coverage_pct = max([p for p in percentages if p <= 100])
                total_reqs = 100
                covered_reqs = int((coverage_pct / 100) * total_reqs)
            else:
                total_reqs = 50
                covered_reqs = 45  # 90% typical compliance
            
            metrics["compliance_coverage"] = {
                "requirements_covered": covered_reqs,
                "total_requirements": total_reqs
            }
        
        # Transaction Anomaly Detection
        if "anomaly" in use_case.lower() or "fraud" in use_case.lower() or "transaction" in use_case.lower():
            # Use percentages from text or defaults
            if percentages:
                detection_rate = max([p for p in percentages if p <= 100])
                total_anomalies = 100
                detected_anomalies = int((detection_rate / 100) * total_anomalies)
            else:
                total_anomalies = 50
                detected_anomalies = 42  # 84% detection rate
            
            metrics["transaction_anomaly"] = {
                "detected_anomalies": detected_anomalies,
                "total_anomalies": total_anomalies
            }
        
        # False Positive Rate
        if "alert" in use_case.lower() or "false" in use_case.lower():
            total_alerts = 1000
            false_positives = 50  # 5% false positive rate (good)
            
            metrics["false_positive"] = {
                "false_positives": false_positives,
                "total_alerts": total_alerts
            }
        
        # Transaction Security Index
        if "transaction" in use_case.lower() or "banking" in use_case.lower():
            metrics["transaction_security"] = {
                "encryption_score": 95.0,
                "authentication_score": 85.0,
                "fraud_detection_score": 80.0
            }
        
        # System Availability
        if "availability" in use_case.lower() or "uptime" in use_case.lower() or "downtime" in use_case.lower():
            # Extract downtime metrics or use defaults
            downtime_minutes = 5.0  # 5 minutes downtime per month (99.99% uptime)
            
            metrics["system_availability"] = {
                "downtime_minutes": downtime_minutes,
                "period_days": 30
            }
        
        # Security Training Effectiveness
        if "training" in use_case.lower() or "education" in use_case.lower():
            # Extract training metrics
            if percentages:
                completion_rate = max([p for p in percentages if p <= 100])
            else:
                completion_rate = 95.0  # Default high completion rate
            
            metrics["security_training"] = {
                "pre_training_score": 65.0,
                "post_training_score": 85.0,
                "completion_rate": completion_rate
            }
        
        # Fraud Detection Efficiency
        if "fraud" in use_case.lower():
            metrics["fraud_detection"] = {
                "detected_fraud_amount": 95000.0,
                "total_fraud_amount": 100000.0,
                "response_time_hours": 2.0
            }
        
        # Encryption Strength Score
        if "encrypt" in use_case.lower() or "aes" in use_case.lower():
            metrics["encryption_strength"] = {
                "encryption_algorithm": "AES",
                "key_length": 256,
                "data_in_transit_encrypted": True,
                "data_at_rest_encrypted": True
            }
        
        # Always include some baseline metrics for core KPIs if not already present
        if "vulnerability_management" not in metrics:
            metrics["vulnerability_management"] = {
                "total_vulnerabilities": 25,
                "addressed_vulnerabilities": 20  # 80% baseline
            }
        
        if "mean_time_to_detect" not in metrics:
            metrics["mean_time_to_detect"] = {
                "detection_times_hours": [1.5, 2.8, 1.2, 3.5, 2.1]  # Baseline detection times
            }
        
        if "mean_time_to_respond" not in metrics:
            metrics["mean_time_to_respond"] = {
                "response_times_hours": [3.0, 4.5, 2.8, 5.2, 3.8]  # Baseline response times
            }
        
        if "security_coverage" not in metrics:
            metrics["security_coverage"] = {
                "coverage_metrics": {
                    "access_control": {"score": 75.0, "implemented": True},
                    "monitoring": {"score": 70.0, "implemented": True},
                    "authentication": {"score": 80.0, "implemented": True}
                }
            }
        
        if "system_availability" not in metrics:
            metrics["system_availability"] = {
                "downtime_minutes": 10.0,  # 10 minutes downtime per month
                "period_days": 30
            }
        
        return metrics

    def _calculate_kpis_with_extracted_metrics(self, extracted_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate KPIs using extracted metrics from the text.
        
        Args:
            extracted_metrics: Dictionary of extracted metrics
            
        Returns:
            Dictionary with calculated KPI scores and analysis
        """
        kpi_scores = {}
        analysis = {}
        
        # Calculate each KPI based on available metrics
        if "vulnerability_management" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "vulnerability_management_effectiveness",
                **extracted_metrics["vulnerability_management"]
            )
            if "error" not in result:
                kpi_scores["vulnerability_management_effectiveness"] = result["score"]
                analysis["vulnerability_management_effectiveness"] = result["details"]
        
        if "mean_time_to_detect" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "mean_time_to_detect",
                **extracted_metrics["mean_time_to_detect"]
            )
            if "error" not in result:
                kpi_scores["mean_time_to_detect"] = result["score"]
                analysis["mean_time_to_detect"] = result["details"]
        
        if "mean_time_to_respond" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "mean_time_to_respond",
                **extracted_metrics["mean_time_to_respond"]
            )
            if "error" not in result:
                kpi_scores["mean_time_to_respond"] = result["score"]
                analysis["mean_time_to_respond"] = result["details"]
        
        if "security_coverage" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "security_coverage_score",
                **extracted_metrics["security_coverage"]
            )
            if "error" not in result:
                kpi_scores["security_coverage_score"] = result["score"]
                analysis["security_coverage_score"] = result["details"]
        
        if "risk_reduction" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "risk_reduction_percentage",
                **extracted_metrics["risk_reduction"]
            )
            if "error" not in result:
                kpi_scores["risk_reduction_percentage"] = result["score"]
                analysis["risk_reduction_percentage"] = result["details"]
        
        if "compliance_coverage" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "compliance_coverage_percentage",
                **extracted_metrics["compliance_coverage"]
            )
            if "error" not in result:
                kpi_scores["compliance_coverage_percentage"] = result["score"]
                analysis["compliance_coverage_percentage"] = result["details"]
        
        if "transaction_anomaly" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "transaction_anomaly_detection_rate",
                **extracted_metrics["transaction_anomaly"]
            )
            if "error" not in result:
                kpi_scores["transaction_anomaly_detection_rate"] = result["score"]
                analysis["transaction_anomaly_detection_rate"] = result["details"]
        
        if "false_positive" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "false_positive_rate",
                **extracted_metrics["false_positive"]
            )
            if "error" not in result:
                kpi_scores["false_positive_rate"] = result["score"]
                analysis["false_positive_rate"] = result["details"]
        
        if "transaction_security" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "transaction_security_index",
                **extracted_metrics["transaction_security"]
            )
            if "error" not in result:
                kpi_scores["transaction_security_index"] = result["score"]
                analysis["transaction_security_index"] = result["details"]
        
        if "system_availability" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "system_availability_percentage",
                **extracted_metrics["system_availability"]
            )
            if "error" not in result:
                kpi_scores["system_availability_percentage"] = result["score"]
                analysis["system_availability_percentage"] = result["details"]
        
        if "security_training" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "security_training_effectiveness",
                **extracted_metrics["security_training"]
            )
            if "error" not in result:
                kpi_scores["security_training_effectiveness"] = result["score"]
                analysis["security_training_effectiveness"] = result["details"]
        
        if "fraud_detection" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "fraud_detection_efficiency",
                **extracted_metrics["fraud_detection"]
            )
            if "error" not in result:
                kpi_scores["fraud_detection_efficiency"] = result["score"]
                analysis["fraud_detection_efficiency"] = result["details"]
        
        if "encryption_strength" in extracted_metrics:
            result = self.calculate_specific_kpi(
                "encryption_strength_score",
                **extracted_metrics["encryption_strength"]
            )
            if "error" not in result:
                kpi_scores["encryption_strength_score"] = result["score"]
                analysis["encryption_strength_score"] = result["details"]
        
        return kpi_scores, analysis
