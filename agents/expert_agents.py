"""
Expert agent implementations for policy evaluation.

This module contains the specialized agents for:
1. Gap checking - identifies missing elements in policies compared to standards
2. Compliance checking - evaluates how well policies comply with standards
3. Enhancement - suggests improvements for policies based on standards
"""
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.base import Agent

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
6. Always provide justification for your classification using evidence from both the policy and standards.

Your output should be in the following format:
{
  "chunk_content": "<The policy chunk you analyzed>",
  "classification": "<GOOD, MISSING, or NON_COMPLIANT>",
  "gaps_identified": ["<List of specific gaps found>"],
  "justification": "<Your detailed reasoning for this classification>",
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
        # Prepare prompt for the LLM
        prompt = f"""
        I need you to analyze this security policy chunk and identify any gaps when compared to the provided standards.
        
        ## POLICY CHUNK:
        {policy_chunk}
        
        ## STANDARDS TO COMPARE AGAINST:
        {standards}
        
        Follow your instructions to identify gaps, classify the chunk, and provide a detailed justification.
        """
        
        # Create messages for the agent
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Get response from LLM
        response = self._invoke_with_retry(messages)
        
        # Return the response content
        return {"analysis": response.content}


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
6. Always provide justification for your classification using evidence from both the policy and standards.

Your output should be in the following format:
{
  "chunk_content": "<The policy chunk you analyzed>",
  "classification": "<GOOD, MISSING, or NON_COMPLIANT>",
  "compliance_issues": ["<List of specific compliance issues found>"],
  "justification": "<Your detailed reasoning for this classification>",
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
        # Prepare prompt for the LLM
        prompt = f"""
        I need you to check the compliance of this security policy chunk against the provided standards.
        
        ## POLICY CHUNK:
        {policy_chunk}
        
        ## STANDARDS TO CHECK AGAINST:
        {standards}
        
        Follow your instructions to check compliance, classify the chunk, and provide a detailed justification.
        """
        
        # Create messages for the agent
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Get response from LLM
        response = self._invoke_with_retry(messages)
        
        # Return the response content
        return {"assessment": response.content}


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
7. Always provide justification for your enhancements, referencing both the original policy and standards.

Your output should be in the following format:
{
  "chunk_content": "<The policy chunk you analyzed>",
  "classification": "<GOOD, MISSING, or NON_COMPLIANT>",
  "enhanced_content": "<The improved policy content with your enhancements>",
  "enhancements": ["<List of specific enhancements made>"],
  "justification": "<Your detailed reasoning for these enhancements>"
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
        """
        
        # Create messages for the agent
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Get response from LLM
        response = self._invoke_with_retry(messages)
        
        # Return the response content
        return {"enhancement": response.content}
