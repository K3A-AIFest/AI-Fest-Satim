"""
Use Case processor orchestrator that coordinates the workflow between expert agents.

This module contains the main pipeline for use case evaluation against standards and policies:
1. Analyze security KPIs for the use case
2. Analyze deployment aspects
3. Judge the quality and effectiveness of the use case
4. Aggregate and synthesize all analyses
"""
import json
import logging
from typing import List, Dict, Any, Optional
from agents.use_case_agents import (

    DeploymentAnalyzerAgent,
    UseCaseJudgeAgent,
    AnalysisAggregatorAgent
)
from tools.vector_db import fetch_relevant_standards, fetch_relevant_policies
from agents.kpi_agent import KPIAgent
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UseCaseProcessingPipeline:
    """
    Orchestrates the use case processing workflow using expert agents.
    """
    
    def __init__(self):
        """
        Initialize the pipeline with expert agents.
        """
        self.kpi_analyzer = KPIAgent()
        self.deployment_analyzer = DeploymentAnalyzerAgent()
        self.use_case_judge = UseCaseJudgeAgent()
        self.analysis_aggregator = AnalysisAggregatorAgent()
        logger.info("Use case processing pipeline initialized with expert agents")
    
    def get_relevant_standards(self, use_case_text: str) -> List[str]:
        """
        Retrieve standards relevant to a use case.
        
        Args:
            use_case_text: The security use case text
            
        Returns:
            List of relevant standard sections
        """
        # Fetch relevant standards
        standards_results = fetch_relevant_standards(use_case_text, top_k=5)
        
        # Extract the content
        standards = [result["content"] for result in standards_results]
        return standards
    
    def get_relevant_policies(self, use_case_text: str) -> List[str]:
        """
        Retrieve policies relevant to a use case.
        
        Args:
            use_case_text: The security use case text
            
        Returns:
            List of relevant policy sections
        """
        # Fetch relevant policies
        policies_results = fetch_relevant_policies(use_case_text, top_k=5)
        
        # Extract the content
        policies = [result["content"] for result in policies_results]
        return policies
    
    def process_use_case(
        self, 
        use_case: str, 
        standards_content: Optional[List[str]] = None,
        policies_content: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a security use case using multiple expert agents.
        
        Args:
            use_case: The security use case text to analyze
            standards_content: Optional list of specific standards to evaluate against
                             (if None, relevant standards will be retrieved automatically)
            policies_content: Optional list of specific policies to evaluate against
                            (if None, relevant policies will be retrieved automatically)
            
        Returns:
            Comprehensive analysis of the use case
        """
        logger.info("Starting use case processing")
        
        # Get relevant standards and policies if not provided
        use_case_standards = standards_content if standards_content else self.get_relevant_standards(use_case)
        use_case_policies = policies_content if policies_content else self.get_relevant_policies(use_case)
        
        # Step 1: Analyze KPIs
        logger.info("Analyzing security KPIs")
        kpi_analysis = self.kpi_analyzer.analyze_security_kpis(
            use_case=use_case,
            standards=use_case_standards,
            policies=use_case_policies
        )
        
        # Step 2: Analyze deployment aspects
        logger.info("Analyzing deployment aspects")
        deployment_analysis = self.deployment_analyzer.analyze_deployment(
            use_case=use_case,
            standards=use_case_standards,
            policies=use_case_policies
        )
        
        # Step 3: Judge the use case
        logger.info("Judging use case quality and effectiveness")
        use_case_judgment = self.use_case_judge.judge_use_case(
            use_case=use_case,
            standards=use_case_standards,
            policies=use_case_policies
        )
        
        # Step 4: Aggregate all analyses
        logger.info("Aggregating analyses for final assessment")
        aggregated_analysis = self.analysis_aggregator.aggregate_analyses(
            use_case=use_case,
            kpi_analysis=kpi_analysis,
            deployment_analysis=deployment_analysis,
            use_case_judgment=use_case_judgment
        )
        
        # Combine all results
        result = {
            "use_case_content": use_case,
            "kpi_analysis": kpi_analysis,
            "deployment_analysis": deployment_analysis,
            "use_case_judgment": use_case_judgment,
            "aggregated_analysis": aggregated_analysis
        }
        
        logger.info("Use case processing complete")
        return result


# Main functions to be called from the API

def analyze_use_case_kpis(use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze security KPIs for a use case.
    
    Args:
        use_case: The security use case text to analyze
        standards: List of standard documents to evaluate against
        policies: Optional list of policy documents to evaluate against
        
    Returns:
        KPI analysis results
    """
    pipeline = UseCaseProcessingPipeline()
    kpi_analyzer = pipeline.kpi_analyzer
    
    # Analyze KPIs
    kpi_analysis = kpi_analyzer.analyze_security_kpis(use_case, standards, policies)
    
    return kpi_analysis

def analyze_deployment(use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze deployment aspects of a use case.
    
    Args:
        use_case: The security use case text to analyze
        standards: List of standard documents to evaluate against
        policies: Optional list of policy documents to evaluate against
        
    Returns:
        Deployment analysis results
    """
    pipeline = UseCaseProcessingPipeline()
    deployment_analyzer = pipeline.deployment_analyzer
    
    # Analyze deployment
    deployment_analysis = deployment_analyzer.analyze_deployment(use_case, standards, policies)
    
    return deployment_analysis

def judge_use_case(use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Judge the quality and effectiveness of a use case.
    
    Args:
        use_case: The security use case text to analyze
        standards: List of standard documents to evaluate against
        policies: Optional list of policy documents to evaluate against
        
    Returns:
        Use case judgment results
    """
    pipeline = UseCaseProcessingPipeline()
    use_case_judge = pipeline.use_case_judge
    
    # Judge use case
    use_case_judgment = use_case_judge.judge_use_case(use_case, standards, policies)
    
    return use_case_judgment

def process_use_case(use_case: str, standards: List[str], policies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Process a use case with all expert agents and aggregate results.
    
    Args:
        use_case: The security use case text to analyze
        standards: List of standard documents to evaluate against
        policies: Optional list of policy documents to evaluate against
        
    Returns:
        Comprehensive use case analysis including KPIs, deployment assessment, 
        judgment, and aggregated results
    """
    pipeline = UseCaseProcessingPipeline()
    result = pipeline.process_use_case(use_case, standards, policies)
    
    return result
