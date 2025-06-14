"""
Use Case Analysis Agent implementations.

This module contains the specialized agents for use case processing:
1. KPI Analysis - analyzes security KPIs for use cases (moved to kpi_agent.py)
2. Deployment Analysis - analyzes deployment aspects of use cases
3. Use Case Judgment - judges quality and effectiveness of use cases
4. Analysis Aggregation - aggregates multiple analyses into comprehensive assessment
"""

from typing import List, Dict, Any, Optional
import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from agents.base import Agent


class DeploymentAnalysisOutput(BaseModel):
    """Structured output for deployment analysis"""
    feasibility_score: float = Field(description="Feasibility score between 0-100")
    pros: List[str] = Field(description="List of advantages for deploying the use case")
    cons: List[str] = Field(description="List of disadvantages or challenges for deploying the use case")
    timeline_estimate: str = Field(description="Estimated timeline for deployment")
    resource_requirements: List[str] = Field(description="List of resources required for deployment")
    risk_factors: List[Dict[str, Any]] = Field(description="List of risk factors with severity and mitigation strategies")


class UseCaseJudgmentOutput(BaseModel):
    """Structured output for use case judgment"""
    effectiveness_score: float = Field(description="Effectiveness score between 0-100")
    alignment_with_standards: List[Dict[str, Any]] = Field(description="Analysis of alignment with referenced standards")
    alignment_with_policies: List[Dict[str, Any]] = Field(description="Analysis of alignment with referenced policies")
    security_impact: str = Field(description="Overall security impact assessment")
    gaps_identified: List[str] = Field(description="List of identified gaps in the use case")
    improvement_suggestions: List[str] = Field(description="List of suggestions to improve the use case")


class AggregatedAnalysisOutput(BaseModel):
    """Structured output for aggregated analysis"""
    overall_assessment: str = Field(description="Overall assessment summary")
    overall_score: float = Field(description="Overall score between 0-100")
    key_findings: List[str] = Field(description="List of key findings from all analyses")
    critical_considerations: List[str] = Field(description="List of critical considerations")
    recommended_next_steps: List[str] = Field(description="Recommended next steps")
    stakeholder_considerations: Dict[str, List[str]] = Field(description="Considerations for different stakeholders")


class DeploymentAnalyzerAgent(Agent):
    """
    Expert agent that analyzes deployment aspects of a security use case.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Deployment Analyzer Agent specializing in assessing the feasibility and implementation aspects of security use cases, particularly for banking and financial systems.
        
Your task is to analyze the deployment considerations for a given security use case with focus on financial industry requirements.

When analyzing deployment aspects of a security use case:
1. Assess the overall feasibility of implementing the use case (score 0-100)
2. Consider banking-specific requirements:
   - Regulatory compliance (PCI-DSS, SOX, Basel III)
   - High availability requirements (99.9%+ uptime)
   - Real-time transaction processing capabilities
   - Integration with core banking systems
   - Security and audit requirements
3. Identify clear pros and cons of deployment
4. Estimate realistic timeline for implementation in a regulated environment
5. List necessary resources (technical, human, financial, compliance) required
6. Identify potential risk factors, their severity, and mitigation strategies
7. Consider integration challenges with legacy financial systems
8. Evaluate scalability for high-volume transaction processing
9. Assess maintenance and operational requirements

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "feasibility_score": 75.0,
  "pros": ["Enhances fraud detection capability", "Improves compliance reporting"],
  "cons": ["Requires significant initial investment", "Complex integration with legacy systems"],
  "timeline_estimate": "6-12 months including regulatory approval",
  "resource_requirements": ["Security engineers (2 FTE)", "Compliance officer (0.5 FTE)", "$500K initial investment"],
  "risk_factors": [
    {
      "risk": "Integration with legacy core banking systems",
      "severity": "High",
      "mitigation": "Develop custom APIs and implement phased rollout with extensive testing"
    }
  ]
}"""

        # Initialize with base Agent class
        super().__init__(system_prompt=system_prompt)
    
    def analyze_deployment(self, use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze deployment aspects of a security use case.
        
        Args:
            use_case: The security use case text to analyze
            standards: List of relevant standard documents to reference
            policies: Optional list of policy documents to reference
            
        Returns:
            Deployment analysis with feasibility, pros/cons, timeline, and resources
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=DeploymentAnalysisOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM
        policies_text = "\n\n".join(policies) if policies else "No specific policies provided."
        standards_text = "\n\n".join(standards)
        
        prompt = f"""
        I need you to analyze the deployment aspects of this security use case for banking/financial systems.
        
        ## USE CASE:
        {use_case}
        
        ## STANDARDS TO REFERENCE:
        {standards_text}
        
        ## POLICIES TO REFERENCE:
        {policies_text}
        
        Focus on banking industry requirements and regulatory considerations.
        Assess deployment feasibility, pros, cons, timeline, resources, and risks.
        
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
                        "feasibility_score": 0,
                        "pros": [],
                        "cons": [f"Error analyzing deployment: {str(e)}"],
                        "timeline_estimate": "Unknown",
                        "resource_requirements": [],
                        "risk_factors": []
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "feasibility_score": 0,
                    "pros": [],
                    "cons": [f"Error analyzing deployment: {str(e)}. Inner error: {str(inner_e)}"],
                    "timeline_estimate": "Unknown",
                    "resource_requirements": [],
                    "risk_factors": []
                }


class UseCaseJudgeAgent(Agent):
    """
    Expert agent that judges the quality and effectiveness of a security use case.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Use Case Judge Agent specializing in evaluating the quality and effectiveness of security use cases for banking and financial systems.
        
Your task is to judge how well a security use case addresses security requirements and aligns with standards and policies in the financial sector.

When judging a security use case:
1. Evaluate the overall effectiveness of the use case (score 0-100)
2. Analyze how well it aligns with financial industry standards:
   - PCI-DSS for payment card security
   - ISO 27001/27002 for information security
   - NIST Cybersecurity Framework
   - FFIEC guidelines for financial institutions
3. Analyze how well it aligns with referenced policies (if provided)
4. Assess the overall security impact of implementing this use case
5. Consider financial industry specific requirements:
   - Transaction integrity and non-repudiation
   - Customer data protection and privacy
   - Fraud prevention and detection
   - Business continuity and disaster recovery
   - Regulatory reporting capabilities
6. Identify any gaps or missing elements in the use case
7. Suggest specific improvements to enhance the use case

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "effectiveness_score": 80.0,
  "alignment_with_standards": [
    {
      "standard": "PCI-DSS 4.0",
      "alignment_score": 85,
      "comments": "Well aligned with card data protection requirements but lacks specific tokenization details"
    }
  ],
  "alignment_with_policies": [
    {
      "policy": "Data Protection Policy",
      "alignment_score": 70,
      "comments": "Generally complies but has gaps in customer data handling procedures"
    }
  ],
  "security_impact": "High positive impact on fraud prevention and customer data protection",
  "gaps_identified": ["Lack of specific tokenization procedures", "Missing incident response integration"],
  "improvement_suggestions": ["Add detailed tokenization requirements", "Integrate with existing incident response procedures"]
}"""

        # Initialize with base Agent class
        super().__init__(system_prompt=system_prompt)
    
    def judge_use_case(self, use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Judge the quality and effectiveness of a security use case.
        
        Args:
            use_case: The security use case text to analyze
            standards: List of relevant standard documents to reference
            policies: Optional list of policy documents to reference
            
        Returns:
            Judgment of the use case with effectiveness score, alignment analysis, and improvement suggestions
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=UseCaseJudgmentOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM
        policies_text = "\n\n".join(policies) if policies else "No specific policies provided."
        standards_text = "\n\n".join(standards)
        
        prompt = f"""
        I need you to judge this security use case based on its effectiveness and alignment with financial industry standards and policies.
        
        ## USE CASE:
        {use_case}
        
        ## STANDARDS TO REFERENCE:
        {standards_text}
        
        ## POLICIES TO REFERENCE:
        {policies_text}
        
        Focus on banking and financial industry requirements.
        Evaluate the use case, its alignment with standards/policies, security impact, gaps, and suggest improvements.
        
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
                        "effectiveness_score": 0,
                        "alignment_with_standards": [],
                        "alignment_with_policies": [],
                        "security_impact": f"Error judging use case: {str(e)}",
                        "gaps_identified": [],
                        "improvement_suggestions": []
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "effectiveness_score": 0,
                    "alignment_with_standards": [],
                    "alignment_with_policies": [],
                    "security_impact": f"Error judging use case: {str(e)}. Inner error: {str(inner_e)}",
                    "gaps_identified": [],
                    "improvement_suggestions": []
                }


class AnalysisAggregatorAgent(Agent):
    """
    Expert agent that aggregates analyses from other expert agents to provide a comprehensive final assessment.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Analysis Aggregator Agent specializing in synthesizing multiple analyses into a cohesive final assessment for banking and financial security implementations.
        
Your task is to review analyses from different experts and provide a comprehensive, unified assessment suitable for financial industry decision-makers.

When aggregating analyses:
1. Look for common themes, agreements, and disagreements across expert analyses
2. Identify the most critical findings and recommendations for financial security
3. Calculate an overall assessment score based on the individual scores (0-100)
4. Provide a balanced summary that considers all perspectives
5. Highlight the most important considerations for financial industry decision-makers:
   - Regulatory compliance implications
   - Risk management impact
   - Customer trust and reputation factors
   - Business continuity considerations
   - Cost-benefit analysis
6. Recommend clear next steps based on the combined analyses
7. Consider different stakeholder perspectives in banking organizations

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "overall_assessment": "Concise executive summary of the aggregated analysis",
  "overall_score": 82.5,
  "key_findings": ["Strong fraud detection capabilities", "Requires significant infrastructure investment"],
  "critical_considerations": ["Regulatory approval timeline", "Integration complexity with legacy systems"],
  "recommended_next_steps": ["Conduct pilot implementation", "Engage with regulatory bodies"],
  "stakeholder_considerations": {
    "executive_management": ["ROI timeline of 18-24 months", "Regulatory compliance benefits"],
    "security_team": ["Integration with existing SIEM tools", "Staff training requirements"],
    "operations_team": ["24/7 monitoring requirements", "Backup and recovery procedures"],
    "compliance": ["PCI-DSS alignment", "Audit trail capabilities"],
    "risk_management": ["Residual risk assessment", "Business impact analysis"]
  }
}"""

        # Initialize with base Agent class
        super().__init__(system_prompt=system_prompt)
    
    def aggregate_analyses(self, use_case: str, kpi_analysis: Dict[str, Any], 
                         deployment_analysis: Dict[str, Any], 
                         use_case_judgment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate multiple expert analyses into a comprehensive final assessment.
        
        Args:
            use_case: The security use case text that was analyzed
            kpi_analysis: Results from KPI analysis
            deployment_analysis: Results from deployment analysis
            use_case_judgment: Results from use case judgment
            
        Returns:
            Comprehensive aggregated analysis with overall assessment, score, and recommendations
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=AggregatedAnalysisOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM
        prompt = f"""
        I need you to aggregate these expert analyses into a comprehensive final assessment of the security use case for banking/financial systems.
        
        ## USE CASE:
        {use_case}
        
        ## KPI ANALYSIS:
        {json.dumps(kpi_analysis, indent=2)}
        
        ## DEPLOYMENT ANALYSIS:
        {json.dumps(deployment_analysis, indent=2)}
        
        ## USE CASE JUDGMENT:
        {json.dumps(use_case_judgment, indent=2)}
        
        Focus on financial industry implications and provide insights for banking stakeholders.
        Synthesize these analyses into a cohesive final assessment.
        
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
                        "overall_assessment": f"Error aggregating analyses: {str(e)}",
                        "overall_score": 0,
                        "key_findings": [],
                        "critical_considerations": [],
                        "recommended_next_steps": [],
                        "stakeholder_considerations": {}
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "overall_assessment": f"Error aggregating analyses: {str(e)}. Inner error: {str(inner_e)}",
                    "overall_score": 0,
                    "key_findings": [],
                    "critical_considerations": [],
                    "recommended_next_steps": [],
                    "stakeholder_considerations": {}
                }
