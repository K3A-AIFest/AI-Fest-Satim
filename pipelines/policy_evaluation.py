"""
Policy evaluation orchestrator that coordinates the workflow between expert agents.

This module contains the main pipeline for policy evaluation against standards:
1. Split policies into chunks
2. For each chunk, run gap analysis
3. For each chunk, run compliance check
4. For each chunk, generate enhancement recommendations
5. Combine results into a structured output
"""
import json
from typing import List, Dict, Any, Optional
from agents.expert_agents import GapCheckerAgent, ComplianceCheckerAgent, PolicyEnhancerAgent
from tools.vector_db import fetch_relevant_policies, fetch_relevant_standards, rewrite_query
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolicyEvaluationPipeline:
    """
    Orchestrates the policy evaluation process using expert agents.
    """
    
    def __init__(self):
        """
        Initialize the pipeline with expert agents.
        """
        self.gap_checker = GapCheckerAgent()
        self.compliance_checker = ComplianceCheckerAgent()
        self.policy_enhancer = PolicyEnhancerAgent()
        logger.info("Policy evaluation pipeline initialized with expert agents")
    
    def chunk_policy(self, policy_content: str, chunk_size: int = 1000) -> List[str]:
        """
        Split a policy document into manageable chunks for evaluation.
        
        Args:
            policy_content: Full policy document text
            chunk_size: Approximate size of each chunk in characters
            
        Returns:
            List of policy chunks
        """
        # Simple chunking by paragraphs first
        paragraphs = policy_content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split policy into {len(chunks)} chunks")
        return chunks
    
    def get_relevant_standards(self, policy_chunk: str) -> List[str]:
        """
        Retrieve standards relevant to a policy chunk.
        
        Args:
            policy_chunk: A section of a policy document
            
        Returns:
            List of relevant standard sections
        """
        # Rewrite the query to better match the standards
        enhanced_query = rewrite_query(policy_chunk)
        
        # Fetch relevant standards
        standards_results = fetch_relevant_standards(enhanced_query, top_k=5)
        
        # Extract the content
        standards = [result["content"] for result in standards_results]
        
        return standards
    
    def evaluate_policy_chunk(self, policy_chunk: str, standards: List[str]) -> Dict[str, Any]:
        """
        Evaluate a single policy chunk against standards.
        
        Args:
            policy_chunk: A section of a policy document
            standards: List of relevant standard sections
            
        Returns:
            Evaluation results including gap analysis, compliance check, and enhancement suggestions
        """
        logger.info("Starting policy chunk evaluation")
        
        # Step 1: Identify gaps
        logger.info("Performing gap analysis")
        gap_analysis = self.gap_checker.analyze_gaps(policy_chunk, standards)
        
        # Step 2: Check compliance
        logger.info("Checking compliance")
        compliance_assessment = self.compliance_checker.check_compliance(policy_chunk, standards)
        
        # Step 3: Suggest enhancements
        logger.info("Generating enhancement suggestions")
        enhancement = self.policy_enhancer.enhance_policy(
            policy_chunk, 
            gap_analysis, 
            compliance_assessment, 
            standards
        )
        
        # Combine results
        result = {
            "chunk_content": policy_chunk,
            "gap_analysis": gap_analysis,
            "compliance_assessment": compliance_assessment,
            "enhancement": enhancement
        }
        
        logger.info("Policy chunk evaluation complete")
        return result
    
    def evaluate_policy(self, policy_content: str, standards_content: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Evaluate an entire policy document against standards.
        
        Args:
            policy_content: Full policy document text
            standards_content: Optional list of specific standards to evaluate against
                             (if None, relevant standards will be retrieved automatically)
            
        Returns:
            List of evaluation results for each policy chunk
        """
        logger.info("Starting policy evaluation")
        
        # Split policy into manageable chunks
        policy_chunks = self.chunk_policy(policy_content)
        
        results = []
        
        # Process each chunk
        for i, chunk in enumerate(policy_chunks):
            logger.info(f"Processing chunk {i+1}/{len(policy_chunks)}")
            
            # Get relevant standards if not provided
            chunk_standards = standards_content if standards_content else self.get_relevant_standards(chunk)
            
            # Evaluate this chunk
            chunk_result = self.evaluate_policy_chunk(chunk, chunk_standards)
            results.append(chunk_result)
        
        logger.info(f"Policy evaluation complete: {len(results)} chunks processed")
        return results


# Functions for the three main tasks

def identify_gaps(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Identify gaps in a policy compared to standards.
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of gaps identified with classification and justification
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy(policy, standards)
    
    # Extract just the gap analysis from the results
    gap_results = []
    for result in evaluation_results:
        try:
            # Parse the gap analysis content
            gap_analysis = result["gap_analysis"]["analysis"]
            # If the content is a JSON string, parse it
            if isinstance(gap_analysis, str):
                if gap_analysis.strip().startswith('{'):
                    try:
                        gap_analysis = json.loads(gap_analysis)
                    except json.JSONDecodeError:
                        pass
            
            gap_results.append({
                "chunk_content": result["chunk_content"],
                "classification": gap_analysis.get("classification", "UNKNOWN") if isinstance(gap_analysis, dict) else "UNKNOWN",
                "gaps_identified": gap_analysis.get("gaps_identified", []) if isinstance(gap_analysis, dict) else [],
                "justification": gap_analysis.get("justification", "") if isinstance(gap_analysis, dict) else gap_analysis,
            })
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing gap analysis result: {e}")
            gap_results.append({
                "chunk_content": result["chunk_content"],
                "classification": "ERROR",
                "gaps_identified": [],
                "justification": f"Error processing result: {str(e)}",
            })
    
    return gap_results

def check_compliance(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Check compliance of a policy against standards.
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of compliance assessments with classification and justification
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy(policy, standards)
    
    # Extract just the compliance assessment from the results
    compliance_results = []
    for result in evaluation_results:
        try:
            # Parse the compliance assessment content
            compliance_assessment = result["compliance_assessment"]["assessment"]
            # If the content is a JSON string, parse it
            if isinstance(compliance_assessment, str):
                if compliance_assessment.strip().startswith('{'):
                    try:
                        compliance_assessment = json.loads(compliance_assessment)
                    except json.JSONDecodeError:
                        pass
            
            compliance_results.append({
                "chunk_content": result["chunk_content"],
                "classification": compliance_assessment.get("classification", "UNKNOWN") if isinstance(compliance_assessment, dict) else "UNKNOWN",
                "compliance_issues": compliance_assessment.get("compliance_issues", []) if isinstance(compliance_assessment, dict) else [],
                "justification": compliance_assessment.get("justification", "") if isinstance(compliance_assessment, dict) else compliance_assessment,
            })
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing compliance assessment result: {e}")
            compliance_results.append({
                "chunk_content": result["chunk_content"],
                "classification": "ERROR",
                "compliance_issues": [],
                "justification": f"Error processing result: {str(e)}",
            })
    
    return compliance_results

def enhance_policy(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Enhance a policy based on standards.
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of enhanced policy chunks with justification
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy(policy, standards)
    
    # Extract just the enhancement from the results
    enhancement_results = []
    for result in evaluation_results:
        try:
            # Parse the enhancement content
            enhancement = result["enhancement"]["enhancement"]
            # If the content is a JSON string, parse it
            if isinstance(enhancement, str):
                if enhancement.strip().startswith('{'):
                    try:
                        enhancement = json.loads(enhancement)
                    except json.JSONDecodeError:
                        pass
            
            enhancement_results.append({
                "chunk_content": result["chunk_content"],
                "classification": enhancement.get("classification", "UNKNOWN") if isinstance(enhancement, dict) else "UNKNOWN",
                "enhanced_content": enhancement.get("enhanced_content", "") if isinstance(enhancement, dict) else "",
                "enhancements": enhancement.get("enhancements", []) if isinstance(enhancement, dict) else [],
                "justification": enhancement.get("justification", "") if isinstance(enhancement, dict) else enhancement,
            })
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing enhancement result: {e}")
            enhancement_results.append({
                "chunk_content": result["chunk_content"],
                "classification": "ERROR",
                "enhanced_content": result["chunk_content"],
                "enhancements": [],
                "justification": f"Error processing result: {str(e)}",
            })
    
    return enhancement_results
