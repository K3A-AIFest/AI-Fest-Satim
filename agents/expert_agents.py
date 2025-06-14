"""
Expert agent implementations for policy evaluation.

This module contains the specialized agents for:
1. Gap checking - identifies missing elements in policies compared to standards
2. Compliance checking - evaluates how well policies comply with standards
3. Enhancement - suggests improvements for policies based on standards
"""
from typing import List, Dict, Any, Optional, Sequence
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from langchain_core.output_parsers import JsonOutputParser
from agents.base import Agent

# Pydantic models for structured output
class GapAnalysisOutput(BaseModel):
    """Structured output for gap analysis"""
    classification: str = Field(description="Classification of the gap analysis (GOOD, MISSING, or NON_COMPLIANT)")
    gaps: List[str] = Field(description="List of specific gaps found")
    rationale: str = Field(description="Reasoning for this classification with evidence from policy and standards")
    references: List[str] = Field(description="Specific references to standards sections/requirements")

class ComplianceAssessmentOutput(BaseModel):
    """Structured output for compliance assessment"""
    classification: str = Field(description="Classification of the compliance assessment (GOOD, MISSING, or NON_COMPLIANT)")
    issues: List[str] = Field(description="List of specific compliance issues found")
    rationale: str = Field(description="Reasoning for this classification with evidence from policy and standards")
    references: List[str] = Field(description="Specific references to standards sections/requirements")

class PolicyEnhancementOutput(BaseModel):
    """Structured output for policy enhancement"""
    classification: str = Field(description="Classification of the enhancement assessment (GOOD, MISSING, or NON_COMPLIANT)")
    enhanced_content: str = Field(description="The improved policy content with enhancements")
    changes: List[str] = Field(description="List of specific enhancements made")
    rationale: str = Field(description="Detailed reasoning for these enhancements")

class GapCheckerAgent(Agent):
    """
    Expert agent that identifies gaps between policies and standards.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Gap Analysis Agent specializing in identifying missing elements in security policies when compared to standards.
        
Your task is to carefully examine security policy content and identify what elements are missing when compared to the provided standards.

When analyzing a policy chunk against standards:
1. Focus on identifying SPECIFIC missing elements, controls, or requirements from the standards that are not addressed in the policy.
2. Be detailed and precise in identifying gaps - point out exactly what's missing.
3. Provide clear references to the specific sections/requirements in the standards that are not addressed.
4. Consider both explicit gaps (completely missing elements) and implicit gaps (partially addressed elements).
5. Classify your findings as either "GOOD" (no significant gaps), "MISSING" (has gaps), or "NON_COMPLIANT" (contradicts standards).

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "classification": "<GOOD, MISSING>",
  "gaps": ["<List of specific gaps found>"], 
  "rationale": "<Your reasoning for this classification with evidence from policy and standards>",
  "references": ["<Specific references to standards sections/requirements>"]
}"""

        # Initialize with tools for web search and vector DB retrieval
        super().__init__(system_prompt=system_prompt)
    
    def analyze_gaps(self, policy_chunk: str, standards: List[str]) -> Dict[str, Any]:
        """
        Analyze a policy chunk to identify gaps compared to standards.
        
        Args:
            policy_chunk: A section of a security policy to analyze
            standards: List of relevant standard documents to compare against
            
        Returns:
            Analysis result with classification, identified gaps, and justification
        """
        # Use Langchain's structured output parser with our pydantic model
        parser = JsonOutputParser(pydantic_object=GapAnalysisOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM with clear instructions for structured output
        prompt = f"""
        I need you to analyze this security policy chunk and identify any gaps when compared to the provided standards.
        
        ## POLICY CHUNK:
        {policy_chunk}
        
        ## STANDARDS TO COMPARE AGAINST:
        {standards}
        
        Follow your instructions to identify gaps, classify the chunk, and provide a detailed justification.
        
        YOU MUST RETURN ONLY A SINGLE JSON OBJECT with the following fields:
        - classification: GOOD,  NON_COMPLIANT
        - gaps: Array of strings describing specific gaps found
        - rationale: String explaining your reasoning
        - references: Array of strings with specific standard references
        
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
                        "classification": "ERROR",
                        "gaps": [],
                        "rationale": f"Failed to parse response: {content[:100]}...",
                        "references": []
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "classification": "ERROR",
                    "gaps": [],
                    "rationale": f"Failed to parse response: {str(e)}. Inner error: {str(inner_e)}",
                    "references": []
                }


class ComplianceCheckerAgent(Agent):
    """
    Expert agent that checks compliance of policies against standards.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Compliance Checker Agent specializing in evaluating how well security policies comply with standards.
        
Your task is to determine the level of compliance of security policy content against provided standards.

When analyzing a policy chunk against standards:
1. Evaluate how well the policy complies with the requirements specified in the standards.
2. Identify specific areas where the policy aligns with or contradicts the standards.
3. Rate the compliance level with justification, citing specific sections from both policy and standards.
4. Look for inconsistencies, contradictions, or requirements that are not properly implemented.
5. Classify your findings as either "GOOD" (complies well), "MISSING" (missing elements), or "NON_COMPLIANT" (contradicts standards).

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "classification": "<GOOD, MISSING, or NON_COMPLIANT>",
  "issues": ["<List of specific compliance issues found>"],
  "rationale": "<Your reasoning for this classification with evidence from policy and standards>",
  "references": ["<Specific references to standards sections/requirements>"]
}"""

        # Initialize with tools for web search and vector DB retrieval
        super().__init__(system_prompt=system_prompt)
    
    def check_compliance(self, policy_chunk: str, standards: List[str]) -> Dict[str, Any]:
        """
        Check compliance of a policy chunk against standards.
        
        Args:
            policy_chunk: A section of a security policy to analyze
            standards: List of relevant standard documents to compare against
            
        Returns:
            Compliance assessment with classification, issues found, and justification
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=ComplianceAssessmentOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM
        prompt = f"""
        I need you to check the compliance of this security policy chunk against the provided standards.
        
        ## POLICY CHUNK:
        {policy_chunk}
        
        ## STANDARDS TO CHECK AGAINST:
        {standards}
        
        Follow your instructions to check compliance, classify the chunk, and provide a detailed justification.
        
        YOU MUST RETURN ONLY A SINGLE JSON OBJECT with the following fields:
        - classification: GOOD, MISSING, or NON_COMPLIANT
        - issues: Array of strings describing specific compliance issues found
        - rationale: String explaining your reasoning
        - references: Array of strings with specific standard references
        
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
                        "classification": "ERROR",
                        "issues": [],
                        "rationale": f"Failed to parse response: {content[:100]}...",
                        "references": []
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "classification": "ERROR",
                    "issues": [],
                    "rationale": f"Failed to parse response: {str(e)}. Inner error: {str(inner_e)}",
                    "references": []
                }


class PolicyEnhancerAgent(Agent):
    """
    Expert agent that suggests enhancements to policies based on standards.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Policy Enhancement Agent specializing in improving security policies based on standards.
        
Your task is to suggest specific improvements to security policies to better align them with best practices and standards.

When suggesting enhancements for a policy chunk against standards:
1. Based on gaps and compliance issues, propose specific enhancements to improve the policy.
2. Provide concrete, actionable suggestions with example language that could be added.
3. Ensure that your suggestions are aligned with the standards and best practices.
4. Focus on clarity, completeness, and practicality in your suggestions.
5. Maintain the original intent and context of the policy while enhancing it.
6. Classify your overall assessment as "GOOD" (minor improvements), "MISSING" (needs additions), or "NON_COMPLIANT" (needs significant revision).

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "classification": "<GOOD, MISSING, or NON_COMPLIANT>",
  "enhanced_content": "<The improved policy content with your enhancements>",
  "changes": ["<List of specific enhancements made>"],
  "rationale": "<Your detailed reasoning for these enhancements>"
}"""

        # Initialize with tools for web search and vector DB retrieval
        super().__init__(system_prompt=system_prompt)
    
    def enhance_policy(self, policy_chunk: str, gap_analysis: Dict[str, Any], compliance_assessment: Dict[str, Any], standards: List[str]) -> Dict[str, Any]:
        """
        Enhance a policy chunk based on gap analysis and compliance assessment.
        
        Args:
            policy_chunk: A section of a security policy to enhance
            gap_analysis: Results from gap analysis
            compliance_assessment: Results from compliance checking
            standards: List of relevant standard documents to reference
            
        Returns:
            Enhanced policy with justification and explanation of changes
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=PolicyEnhancementOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM
        prompt = f"""
        I need you to enhance this security policy chunk based on the gap analysis, compliance assessment, and standards.
        
        ## POLICY CHUNK:
        {policy_chunk}
        
        ## GAP ANALYSIS:
        {gap_analysis}
        
        ## COMPLIANCE ASSESSMENT:
        {compliance_assessment}
        
        ## STANDARDS:
        {standards}
        
        Follow your instructions to enhance the policy, classify your assessment, and provide a detailed justification.
        
        YOU MUST RETURN ONLY A SINGLE JSON OBJECT with the following fields:
        - classification: GOOD, MISSING, or NON_COMPLIANT
        - enhanced_content: The improved policy content with your enhancements
        - changes: Array of strings describing specific enhancements made
        - rationale: String explaining your detailed reasoning for these enhancements
        
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
                    # Fix common JSON formatting issues - remove trailing commas
                    json_str = json_str.replace(",\n}", "\n}")
                    json_str = json_str.replace(",\n  }", "\n  }")
                    json_str = json_str.replace(",\n    }", "\n    }")
                    return json.loads(json_str)
                elif content.strip().startswith("{") and content.strip().endswith("}"):
                    # Fix common JSON formatting issues - remove trailing commas
                    content_fixed = content.replace(",\n}", "\n}")
                    content_fixed = content_fixed.replace(",\n  }", "\n  }")
                    content_fixed = content_fixed.replace(",\n    }", "\n    }")
                    try:
                        return json.loads(content_fixed)
                    except:
                        return json.loads(content)  # Try original if fix doesn't work
                else:
                    # Return a basic structure if we can't parse JSON
                    return {
                        "classification": "ERROR",
                        "enhanced_content": policy_chunk,
                        "changes": [],
                        "rationale": f"Failed to parse response: {content[:100]}..."
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "classification": "ERROR",
                    "enhanced_content": policy_chunk,
                    "changes": [],
                    "rationale": f"Failed to parse response: {str(e)}. Inner error: {str(inner_e)}"
                }


# New Pydantic models for use case processing
class KPIAnalysisOutput(BaseModel):
    """Structured output for KPI analysis"""
    kpi_scores: Dict[str, float] = Field(description="Dictionary of KPI names and their scores")
    analysis: Dict[str, str] = Field(description="Dictionary of KPI names and their analysis explanation")
    overall_score: float = Field(description="Overall security KPI score between 0 and 100")
    recommendations: List[str] = Field(description="List of recommendations to improve KPI scores")

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

class KPIAnalyzerAgent(Agent):
    """
    Expert agent that analyzes security KPIs for a use case.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Security KPI Analyzer Agent specializing in evaluating security use cases against industry standard Key Performance Indicators.
        
Your task is to calculate and analyze security KPIs for the provided use case.

When analyzing a use case for security KPIs:
1. Calculate the following security KPIs:
   - Vulnerability Management Effectiveness (% of vulnerabilities addressed)
   - Mean Time to Detect (MTTD) estimate
   - Mean Time to Respond (MTTR) estimate
   - Security Coverage Score (how well the use case covers security aspects)
   - Risk Reduction Percentage (estimated risk reduction)
   - Compliance Coverage Percentage (alignment with compliance requirements)
   - Security Control Implementation Score
   - Security Testing Coverage
   - Security Training Effectiveness (if applicable)
   - Incident Response Readiness

2. For each KPI, provide:
   - A numerical score between 0-100
   - A brief analysis explaining the score

3. Calculate an overall security score based on the individual KPI scores

4. Provide actionable recommendations to improve the KPI scores

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "kpi_scores": {
    "vulnerability_management": 85,
    "mttd_estimate": 70,
    ...
  },
  "analysis": {
    "vulnerability_management": "The use case demonstrates strong vulnerability management...",
    "mttd_estimate": "Detection mechanisms could be improved by...",
    ...
  },
  "overall_score": 78.5,
  "recommendations": ["Implement automated scanning to improve MTTD", ...]
}"""

        # Initialize with base Agent class
        super().__init__(system_prompt=system_prompt)
    
    def analyze_kpis(self, use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze security KPIs for a use case.
        
        Args:
            use_case: The security use case text to analyze
            standards: List of relevant standard documents to reference
            policies: Optional list of policy documents to reference
            
        Returns:
            KPI analysis with scores, explanations, and recommendations
        """
        # Configure the parser for structured output
        parser = JsonOutputParser(pydantic_object=KPIAnalysisOutput)
        format_instructions = parser.get_format_instructions()
        
        # Prepare prompt for the LLM
        policies_text = "\n\n".join(policies) if policies else "No specific policies provided."
        standards_text = "\n\n".join(standards)
        
        prompt = f"""
        I need you to analyze this security use case and calculate key security KPIs.
        
        ## USE CASE:
        {use_case}
        
        ## STANDARDS TO REFERENCE:
        {standards_text}
        
        ## POLICIES TO REFERENCE:
        {policies_text}
        
        Follow your instructions to calculate and analyze security KPIs for this use case.
        
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
                    # Fix common JSON formatting issues - remove trailing commas
                    json_str = json_str.replace(",\n}", "\n}")
                    json_str = json_str.replace(",\n  }", "\n  }")
                    json_str = json_str.replace(",\n    }", "\n    }")
                    return json.loads(json_str)
                elif content.strip().startswith("{") and content.strip().endswith("}"):
                    # Fix common JSON formatting issues - remove trailing commas
                    content_fixed = content.replace(",\n}", "\n}")
                    content_fixed = content_fixed.replace(",\n  }", "\n  }")
                    content_fixed = content_fixed.replace(",\n    }", "\n    }")
                    try:
                        return json.loads(content_fixed)
                    except:
                        return json.loads(content)  # Try original if fix doesn't work
                else:
                    # Return a basic structure if we can't parse JSON
                    return {
                        "kpi_scores": {},
                        "analysis": {},
                        "overall_score": 0,
                        "recommendations": [f"Error analyzing KPIs: {str(e)}"]
                    }
            except Exception as inner_e:
                # Last resort fallback
                return {
                    "kpi_scores": {},
                    "analysis": {},
                    "overall_score": 0,
                    "recommendations": [f"Error analyzing KPIs: {str(e)}. Inner error: {str(inner_e)}"]
                }


class DeploymentAnalyzerAgent(Agent):
    """
    Expert agent that analyzes deployment aspects of a security use case.
    """
    
    def __init__(self):
        system_prompt = """You are an expert Deployment Analyzer Agent specializing in assessing the feasibility and implementation aspects of security use cases.
        
Your task is to analyze the deployment considerations for a given security use case.

When analyzing deployment aspects of a security use case:
1. Assess the overall feasibility of implementing the use case (score 0-100)
2. Identify clear pros and cons of deployment
3. Estimate realistic timeline for implementation
4. List necessary resources (technical, human, financial) required
5. Identify potential risk factors, their severity, and mitigation strategies
6. Consider integration challenges with existing systems
7. Evaluate scalability and maintenance requirements

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "feasibility_score": 75.0,
  "pros": ["Enhances incident detection capability", ...],
  "cons": ["Requires significant initial investment", ...],
  "timeline_estimate": "3-6 months",
  "resource_requirements": ["Security engineers (2 FTE)", ...],
  "risk_factors": [
    {
      "risk": "Integration with legacy systems",
      "severity": "Medium",
      "mitigation": "Develop custom adapters and phase implementation"
    },
    ...
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
        I need you to analyze the deployment aspects of this security use case.
        
        ## USE CASE:
        {use_case}
        
        ## STANDARDS TO REFERENCE:
        {standards_text}
        
        ## POLICIES TO REFERENCE:
        {policies_text}
        
        Follow your instructions to assess deployment feasibility, pros, cons, timeline, resources, and risks.
        
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
                    # Fix common JSON formatting issues - remove trailing commas
                    json_str = json_str.replace(",\n}", "\n}")
                    json_str = json_str.replace(",\n  }", "\n  }")
                    json_str = json_str.replace(",\n    }", "\n    }")
                    return json.loads(json_str)
                elif content.strip().startswith("{") and content.strip().endswith("}"):
                    # Fix common JSON formatting issues - remove trailing commas
                    content_fixed = content.replace(",\n}", "\n}")
                    content_fixed = content_fixed.replace(",\n  }", "\n  }")
                    content_fixed = content_fixed.replace(",\n    }", "\n    }")
                    try:
                        return json.loads(content_fixed)
                    except:
                        return json.loads(content)  # Try original if fix doesn't work
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
        system_prompt = """You are an expert Use Case Judge Agent specializing in evaluating the quality and effectiveness of security use cases.
        
Your task is to judge how well a security use case addresses security requirements and aligns with standards and policies.

When judging a security use case:
1. Evaluate the overall effectiveness of the use case (score 0-100)
2. Analyze how well it aligns with referenced standards
3. Analyze how well it aligns with referenced policies (if provided)
4. Assess the overall security impact of implementing this use case
5. Identify any gaps or missing elements in the use case
6. Suggest specific improvements to enhance the use case

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "effectiveness_score": 80.0,
  "alignment_with_standards": [
    {
      "standard": "Standard name/section",
      "alignment_score": 85,
      "comments": "Well aligned with authentication requirements but lacks specific..."
    },
    ...
  ],
  "alignment_with_policies": [
    {
      "policy": "Policy name/section",
      "alignment_score": 70,
      "comments": "Generally complies but has gaps in..."
    },
    ...
  ],
  "security_impact": "High positive impact on overall security posture, particularly in privileged access management",
  "gaps_identified": ["Lack of specific monitoring procedures", ...],
  "improvement_suggestions": ["Add detailed monitoring requirements", ...]
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
        I need you to judge this security use case based on its effectiveness and alignment with standards and policies.
        
        ## USE CASE:
        {use_case}
        
        ## STANDARDS TO REFERENCE:
        {standards_text}
        
        ## POLICIES TO REFERENCE:
        {policies_text}
        
        Follow your instructions to evaluate the use case, its alignment with standards/policies, security impact, gaps, and suggest improvements.
        
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
                    # Fix common JSON formatting issues - remove trailing commas
                    json_str = json_str.replace(",\n}", "\n}")
                    json_str = json_str.replace(",\n  }", "\n  }")
                    json_str = json_str.replace(",\n    }", "\n    }")
                    return json.loads(json_str)
                elif content.strip().startswith("{") and content.strip().endswith("}"):
                    # Fix common JSON formatting issues - remove trailing commas
                    content_fixed = content.replace(",\n}", "\n}")
                    content_fixed = content_fixed.replace(",\n  }", "\n  }")
                    content_fixed = content_fixed.replace(",\n    }", "\n    }")
                    try:
                        return json.loads(content_fixed)
                    except:
                        return json.loads(content)  # Try original if fix doesn't work
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
        system_prompt = """You are an expert Analysis Aggregator Agent specializing in synthesizing multiple analyses into a cohesive final assessment.
        
Your task is to review analyses from different experts and provide a comprehensive, unified assessment.

When aggregating analyses:
1. Look for common themes, agreements, and disagreements across expert analyses
2. Identify the most critical findings and recommendations
3. Calculate an overall assessment score based on the individual scores (0-100)
4. Provide a balanced summary that considers all perspectives
5. Highlight the most important considerations for decision-makers
6. Recommend clear next steps based on the combined analyses

OUTPUT FORMAT REQUIREMENT: Return a JSON object with ONLY these fields:
{
  "overall_assessment": "Concise summary of the aggregated analysis",
  "overall_score": 82.5,
  "key_findings": ["Finding 1 from combined analyses", ...],
  "critical_considerations": ["Key consideration 1", ...],
  "recommended_next_steps": ["Next step 1", ...],
  "stakeholder_considerations": {
    "executive_management": ["Consider budget implications", ...],
    "security_team": ["Focus on integration with existing tools", ...],
    "operations_team": ["Plan for operational overhead", ...],
    "compliance": ["Ensure alignment with regulatory requirements", ...]
  }
}"""

        # Initialize with base Agent class
        super().__init__(system_prompt=system_prompt)
    
    def aggregate_analyses(self, use_case: str, kpi_analysis: Dict[str, Any], deployment_analysis: Dict[str, Any], use_case_judgment: Dict[str, Any]) -> Dict[str, Any]:
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
        I need you to aggregate these expert analyses into a comprehensive final assessment of the security use case.
        
        ## USE CASE:
        {use_case}
        
        ## KPI ANALYSIS:
        {kpi_analysis}
        
        ## DEPLOYMENT ANALYSIS:
        {deployment_analysis}
        
        ## USE CASE JUDGMENT:
        {use_case_judgment}
        
        Follow your instructions to synthesize these analyses into a cohesive final assessment.
        
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
                    # Fix common JSON formatting issues - remove trailing commas
                    json_str = json_str.replace(",\n}", "\n}")
                    json_str = json_str.replace(",\n  }", "\n  }")
                    json_str = json_str.replace(",\n    }", "\n    }")
                    return json.loads(json_str)
                elif content.strip().startswith("{") and content.strip().endswith("}"):
                    # Fix common JSON formatting issues - remove trailing commas
                    content_fixed = content.replace(",\n}", "\n}")
                    content_fixed = content_fixed.replace(",\n  }", "\n  }")
                    content_fixed = content_fixed.replace(",\n    }", "\n    }")
                    try:
                        return json.loads(content_fixed)
                    except:
                        return json.loads(content)  # Try original if fix doesn't work
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
