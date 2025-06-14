# Security KPI Functions and Agent Refactoring

## Overview

This document describes the implementation of KPI functions for security and deployment of information systems, particularly for banking and financial transaction systems, along with the refactoring of the expert agent architecture.

## Changes Made

### 1. KPI Functions Implementation (`tools/kpi.py`)

The KPI functions are already well-implemented and include the following security and financial system KPIs:

#### Security KPIs
- **Vulnerability Management Effectiveness**: Measures how effectively vulnerabilities are addressed
- **Mean Time to Detect (MTTD)**: Average time to detect security incidents
- **Mean Time to Respond (MTTR)**: Average time to respond to security incidents
- **Security Coverage Score**: Overall security coverage assessment
- **Risk Reduction Percentage**: Effectiveness of risk mitigation measures
- **Compliance Coverage Percentage**: Alignment with regulatory requirements

#### Financial System Specific KPIs
- **Transaction Anomaly Detection Rate**: Effectiveness in detecting fraudulent transactions
- **False Positive Rate**: Accuracy of security alerts (lower is better)
- **Transaction Security Index**: Comprehensive security score for financial transactions
- **System Availability Percentage**: Uptime metrics critical for financial systems
- **Security Training Effectiveness**: Effectiveness of security awareness programs
- **Fraud Detection Efficiency**: Speed and accuracy of fraud detection systems
- **Encryption Strength Score**: Assessment of encryption implementation

### 2. Tool Integration (`tools/index.py`)

Updated the tool index to properly manage KPI tools:

```python
def get_all_tools() -> List[Dict[str, Any]]:
    """Returns all available tools including KPI functions"""
    
def get_base_tools() -> List[Dict[str, Any]]:
    """Returns base tools without KPI functions"""
    
def get_kpi_only_tools() -> List[Dict[str, Any]]:
    """Returns only KPI calculation tools"""
    
def get_tools_for_kpi_agent() -> List[Dict[str, Any]]:
    """Returns tools specifically for KPI agent (base + KPI tools)"""
```

### 3. KPI Agent Implementation (`agents/kpi_agent.py`)

Created a specialized KPI agent that:
- **Only binds KPI tools** (not available to other agents)
- Focuses on banking and financial security metrics
- Provides comprehensive KPI analysis with risk assessment
- Includes specific recommendations for financial systems
- Calculates overall security scores with financial industry weights

Key features:
```python
class KPIAgent(Agent):
    def analyze_security_kpis(self, use_case, system_data, standards, policies)
    def calculate_specific_kpi(self, kpi_name, **kwargs)
    def get_kpi_recommendations(self, kpi_scores)
```

### 4. Agent Architecture Refactoring

#### Expert Agents (`agents/evaluation_agents.py`)
Now only contains **policy evaluation agents**:
- `GapCheckerAgent`: Identifies gaps between policies and standards
- `ComplianceCheckerAgent`: Evaluates policy compliance
- `PolicyEnhancerAgent`: Suggests policy improvements

#### Use Case Agents (`agents/use_case_agents.py`)
New file containing **use case analysis agents**:
- `DeploymentAnalyzerAgent`: Analyzes deployment feasibility for financial systems
- `UseCaseJudgeAgent`: Judges quality and effectiveness of use cases
- `AnalysisAggregatorAgent`: Aggregates multiple analyses

#### Base Agent (`agents/base.py`)
Updated to:
- Only bind base tools by default
- Allow specific tools to be added during initialization
- Prevent automatic KPI tool binding for all agents

### 5. Financial Industry Focus

All agents now include specific considerations for banking and financial systems:

#### Banking-Specific Requirements
- **Regulatory Compliance**: PCI-DSS, SOX, Basel III, FFIEC guidelines
- **High Availability**: 99.9%+ uptime requirements
- **Real-time Processing**: Transaction monitoring capabilities
- **Risk Management**: Comprehensive risk assessment frameworks
- **Audit Requirements**: Detailed audit trail capabilities

#### Security Priorities
- Transaction integrity and non-repudiation
- Customer data protection and privacy
- Fraud prevention and detection
- Business continuity and disaster recovery
- Regulatory reporting capabilities

## Usage Examples

### Using the KPI Agent

```python
from agents.kpi_agent import KPIAgent

# Initialize KPI agent (automatically binds KPI tools)
kpi_agent = KPIAgent()

# Analyze security KPIs for a use case
result = kpi_agent.analyze_security_kpis(
    use_case="Implementation of real-time fraud detection system",
    system_data={
        "transaction_volume": 10000000,
        "detection_time_hours": [0.5, 1.2, 0.8],
        "response_time_hours": [2.0, 1.5, 3.0]
    },
    standards=["PCI-DSS 4.0", "ISO 27001"],
    policies=["Data Protection Policy", "Incident Response Policy"]
)

# Calculate specific KPI
vulnerability_kpi = kpi_agent.calculate_specific_kpi(
    "vulnerability_management_effectiveness",
    total_vulnerabilities=100,
    addressed_vulnerabilities=85
)
```

### Using Use Case Analysis Agents

```python
from agents.use_case_agents import DeploymentAnalyzerAgent, UseCaseJudgeAgent

# Deployment analysis
deployment_agent = DeploymentAnalyzerAgent()
deployment_result = deployment_agent.analyze_deployment(
    use_case="Multi-factor authentication for online banking",
    standards=["NIST 800-63B", "PCI-DSS"],
    policies=["Authentication Policy"]
)

# Use case judgment
judge_agent = UseCaseJudgeAgent()
judgment_result = judge_agent.judge_use_case(
    use_case="Real-time transaction monitoring system",
    standards=["ISO 27001", "FFIEC Guidelines"],
    policies=["Transaction Monitoring Policy"]
)
```

## Tool Binding Strategy

### KPI Agent Only
- **KPI tools are exclusively bound to the KPI agent**
- Other agents do not have access to KPI calculation functions
- This prevents tool pollution and ensures clean separation of concerns

### Base Tools for All Agents
- Web search capabilities
- Vector database retrieval (policies and standards)
- Query rewriting functionality

### Specialized Tools
- Each agent type can have additional specialized tools as needed
- Tools are bound during agent initialization based on agent type

## Benefits

1. **Clean Architecture**: Clear separation between policy evaluation and KPI analysis
2. **Financial Focus**: Specialized for banking and financial security requirements
3. **Comprehensive KPIs**: Industry-standard metrics for security assessment
4. **Scalable Design**: Easy to add new agents and tools without conflicts
5. **Regulatory Compliance**: Built-in consideration for financial regulations
6. **Risk Assessment**: Comprehensive risk evaluation capabilities

## Security Considerations

- All KPI calculations use industry-standard formulas
- Financial system requirements prioritized (99.9%+ availability)
- Encryption strength assessments use current best practices
- Fraud detection metrics align with banking industry standards
- Compliance coverage includes major financial regulations

## Future Enhancements

1. **Additional KPIs**: Can easily add new financial security metrics
2. **Real-time Integration**: Connect with actual system monitoring data
3. **Benchmarking**: Compare against industry benchmarks
4. **Automated Reporting**: Generate compliance and security reports
5. **Dashboard Integration**: Visualize KPI trends and alerts
