import json
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

# Import existing models
from src.agent_creator.crew import AgentDefinition, TaskDefinition

# Define CrewPlan model
class CrewPlan:
    """A plan for a crew with agents, tasks and process type."""
    
    def __init__(self, agents: List[AgentDefinition], tasks: List[TaskDefinition], process: str = "sequential"):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.name = f"Generated Crew"
        self.domain = ""
        self.problem_context = ""
        self.input_context = ""
        self.output_context = ""
        self.input_schema = None
        self.output_schema = None

# Define simplified models (without BaseModel inheritance)
class AnalysisResult:
    """Results from the Analysis Crew."""
    def __init__(self, 
                 constraints: List[str] = None,
                 requirements: List[str] = None, 
                 complexity: int = 5,
                 domain_knowledge: List[str] = None,
                 time_sensitivity: Dict[str, Any] = None,
                 success_criteria: List[str] = None,
                 recommended_process_type: str = "sequential"):
        self.constraints = constraints or []
        self.requirements = requirements or []
        self.complexity = complexity
        self.domain_knowledge = domain_knowledge or []
        self.time_sensitivity = time_sensitivity or {}
        self.success_criteria = success_criteria or []
        self.recommended_process_type = recommended_process_type
    
    def dict(self):
        return {
            "constraints": self.constraints,
            "requirements": self.requirements,
            "complexity": self.complexity,
            "domain_knowledge": self.domain_knowledge,
            "time_sensitivity": self.time_sensitivity,
            "success_criteria": self.success_criteria,
            "recommended_process_type": self.recommended_process_type
        }

class PlanningResult:
    """Results from the Planning Crew."""
    def __init__(self,
                 selected_algorithm: str,
                 algorithm_justification: str,
                 candidate_plans: List[Dict[str, Any]] = None,
                 selected_plan: Dict[str, Any] = None,
                 verification_score: int = 0):
        self.selected_algorithm = selected_algorithm
        self.algorithm_justification = algorithm_justification
        self.candidate_plans = candidate_plans or []
        self.selected_plan = selected_plan or {}
        self.verification_score = verification_score
    
    def dict(self):
        return {
            "selected_algorithm": self.selected_algorithm,
            "algorithm_justification": self.algorithm_justification,
            "candidate_plans": self.candidate_plans,
            "selected_plan": self.selected_plan,
            "verification_score": self.verification_score
        }

class ImplementationResult:
    """Results from the Implementation Crew."""
    def __init__(self,
                 agents: List[Dict[str, Any]] = None,
                 tasks: List[Dict[str, Any]] = None,
                 workflow: Dict[str, Any] = None,
                 process_type: str = "sequential",
                 tools: List[Dict[str, Any]] = None):
        self.agents = agents or []
        self.tasks = tasks or []
        self.workflow = workflow or {}
        self.process_type = process_type
        self.tools = tools or []
    
    def dict(self):
        return {
            "agents": self.agents,
            "tasks": self.tasks,
            "workflow": self.workflow,
            "process_type": self.process_type,
            "tools": self.tools
        }

class EvaluationResult:
    """Results from the Evaluation Crew."""
    def __init__(self,
                 strengths: List[str] = None,
                 weaknesses: List[str] = None,
                 missing_elements: List[str] = None,
                 recommendations: List[str] = None,
                 overall_score: int = 0,
                 improvement_area: str = ""):
        self.strengths = strengths or []
        self.weaknesses = weaknesses or []
        self.missing_elements = missing_elements or []
        self.recommendations = recommendations or []
        self.overall_score = overall_score
        self.improvement_area = improvement_area
    
    def dict(self):
        return {
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "missing_elements": self.missing_elements,
            "recommendations": self.recommendations,
            "overall_score": self.overall_score,
            "improvement_area": self.improvement_area
        }

class MultiCrewState:
    """State model for multi-crew workflow processes."""
    def __init__(self):
        self.id = "mock-flow-id"
        self.analysis_result = None
        self.planning_result = None
        self.implementation_result = None
        self.evaluation_result = None
        self.final_plan = None
        
        # Iteration tracking
        self.analysis_iterations = 0
        self.planning_iterations = 0
        self.implementation_iterations = 0
        self.evaluation_iterations = 0
        
        # History tracking
        self.iteration_history = []


class MultiCrewFlow:
    """Flow that orchestrates multiple specialized crews."""
    
    def __init__(self, user_task: str = "", config: Dict[str, Any] = None):
        """Initialize the flow with configuration."""
        self.user_task = user_task
        self.config = config or {}
        self.state = MultiCrewState()
        
        # Default config values
        self.model = self.config.get("model_name", "gpt-4o")
        self.temperature = self.config.get("temperature", 0.7)
    
    def run(self, user_task: str):
        """Run the flow process with the given user task."""
        self.user_task = user_task
        print(f"Starting Multi-Crew Flow for task: {self.user_task}")
        return self.kickoff()
        
    def kickoff(self):
        """Kickoff the flow process with domain-specific implementation."""
        print(f"Processing task with Multi-Crew Flow: {self.user_task}")
        
        domain = self.config.get("domain", "General")
        process_areas = self.config.get("process_areas", [])
        problem_context = self.config.get("problem_context", "")
        input_context = self.config.get("input_context", "")
        output_context = self.config.get("output_context", "")
        constraints = self.config.get("constraints", [])
        
        # Create domain-specific agents
        if "Item-Setup" in process_areas:
            agents = self.create_catalog_setup_agents()
        elif "Compliance" in process_areas:
            agents = self.create_compliance_agents()
        else:
            agents = self.create_default_agents()
        
        # Create domain-specific tasks
        if "Item-Setup" in process_areas:
            tasks = self.create_catalog_setup_tasks()
        elif "Compliance" in process_areas:
            tasks = self.create_compliance_tasks()
        else:
            tasks = self.create_default_tasks()
        
        # Create crew plan
        crew_plan = CrewPlan(
            agents=agents, 
            tasks=tasks,
            process="sequential"
        )
        
        # Set additional properties
        crew_plan.name = f"Generated Crew for {domain}"
        crew_plan.domain = domain
        crew_plan.problem_context = problem_context
        crew_plan.input_context = input_context
        crew_plan.output_context = output_context
        
        # Create basic schema structure
        crew_plan.input_schema = self.create_input_schema(domain, problem_context, input_context)
        crew_plan.output_schema = self.create_output_schema(domain, output_context)
        
        # Store in state
        self.state.final_plan = crew_plan
        
        return crew_plan
    
    def create_catalog_setup_agents(self):
        """Create agents for catalog setup process."""
        return [
            AgentDefinition(
                name="Product Catalog Manager",
                role="Oversee the entire product catalog management process",
                goal="Ensure efficient and accurate product data management",
                backstory="Experienced in retail catalog systems with deep knowledge of product information management"
            ),
            AgentDefinition(
                name="Data Standardization Specialist",
                role="Define and enforce data standards for product attributes",
                goal="Create consistent and high-quality product data",
                backstory="Expert in data modeling and product attribute taxonomies for retail industries"
            ),
            AgentDefinition(
                name="Media Asset Coordinator",
                role="Manage product images and other media assets",
                goal="Ensure all products have complete and high-quality visual assets",
                backstory="Background in digital asset management with expertise in retail imagery standards"
            )
        ]
    
    def create_compliance_agents(self):
        """Create agents for compliance process."""
        return [
            AgentDefinition(
                name="Compliance Officer",
                role="Oversee regulatory compliance across all products",
                goal="Ensure all products meet applicable regulations and standards",
                backstory="Expert in retail compliance with extensive knowledge of product safety and labeling requirements"
            ),
            AgentDefinition(
                name="Documentation Specialist",
                role="Manage compliance documentation and certification",
                goal="Maintain comprehensive records of compliance verification",
                backstory="Detail-oriented professional with experience in regulatory documentation management"
            ),
            AgentDefinition(
                name="Compliance Auditor",
                role="Perform systematic audits of product compliance",
                goal="Identify and flag potential compliance issues before they become problems",
                backstory="Former regulatory inspector with deep knowledge of audit methodologies"
            )
        ]
    
    def create_default_agents(self):
        """Create default agents when no specific process area is specified."""
        return [
            AgentDefinition(
                name="Workflow Manager",
                role="Coordinate workflow and process execution",
                goal="Ensure efficient operation of business processes",
                backstory="Experienced process improvement specialist with expertise in workflow optimization"
            ),
            AgentDefinition(
                name="Data Analyst",
                role="Analyze and validate data throughout the process",
                goal="Ensure data quality and provide actionable insights",
                backstory="Data professional with experience in business intelligence and data governance"
            ),
            AgentDefinition(
                name="Quality Assurance Specialist",
                role="Verify output quality and compliance with requirements",
                goal="Maintain high standards of quality throughout the process",
                backstory="Detail-oriented professional with expertise in quality management systems"
            )
        ]
    
    def create_catalog_setup_tasks(self):
        """Create tasks for catalog setup process."""
        return [
            {
                "name": "Collect and validate product data",
                "purpose": "Gather all required product information from suppliers and validate against data standards",
                "dependencies": [],
                "complexity": "Medium"
            },
            {
                "name": "Standardize product attributes",
                "purpose": "Apply data standards to product attributes and transform into consistent format",
                "dependencies": ["Collect and validate product data"],
                "complexity": "High"
            },
            TaskDefinition(
                name="Process and optimize media assets",
                purpose="Prepare, optimize, and associate media assets with product records",
                dependencies=["Collect and validate product data"],
                complexity="Medium"
            ),
            TaskDefinition(
                name="Final product record verification",
                purpose="Perform comprehensive quality check on complete product records",
                dependencies=["Standardize product attributes", "Process and optimize media assets"],
                complexity="Low"
            )
        ]
    
    def create_compliance_tasks(self):
        """Create tasks for compliance process."""
        return [
            TaskDefinition(
                name="Identify applicable regulations",
                purpose="Determine which regulations apply to the product based on category, materials, and markets",
                dependencies=[],
                complexity="High"
            ),
            TaskDefinition(
                name="Verify compliance documentation",
                purpose="Review and validate compliance documentation and certifications",
                dependencies=["Identify applicable regulations"],
                complexity="Medium"
            ),
            TaskDefinition(
                name="Perform compliance audit",
                purpose="Conduct systematic audit against all applicable requirements",
                dependencies=["Verify compliance documentation"],
                complexity="High"
            ),
            TaskDefinition(
                name="Generate compliance verification report",
                purpose="Compile final compliance status with recommendations for any issues",
                dependencies=["Perform compliance audit"],
                complexity="Medium"
            )
        ]
    
    def create_default_tasks(self):
        """Create default tasks when no specific process area is specified."""
        return [
            TaskDefinition(
                name="Analyze requirements and data",
                purpose="Review all requirements and input data to establish processing plan",
                dependencies=[],
                complexity="Medium"
            ),
            TaskDefinition(
                name="Process and transform data",
                purpose="Execute data transformation according to requirements",
                dependencies=["Analyze requirements and data"],
                complexity="High"
            ),
            TaskDefinition(
                name="Validate results",
                purpose="Verify outputs against requirements and quality standards",
                dependencies=["Process and transform data"],
                complexity="Medium"
            ),
            TaskDefinition(
                name="Generate final deliverables",
                purpose="Prepare final output in required format with documentation",
                dependencies=["Validate results"],
                complexity="Medium"
            )
        ]
    
    def create_input_schema(self, domain, problem_context, input_context):
        """Create a basic input schema structure."""
        class InputSchema:
            def __init__(self):
                self.type = "object"
                self.properties = {
                    "domain": {
                        "type": "string",
                        "description": f"The domain context ({domain})",
                        "example": domain
                    },
                    "problem_context": {
                        "type": "string",
                        "description": "Detailed description of the problem being solved",
                        "example": problem_context
                    },
                    "input_data": {
                        "type": "object",
                        "description": f"The input data: {input_context}",
                        "example": {"sample": "data"}
                    }
                }
                self.required = ["domain", "problem_context", "input_data"]
            
            def model_dump(self):
                return {
                    "type": self.type,
                    "properties": self.properties,
                    "required": self.required
                }
        
        return InputSchema()
    
    def create_output_schema(self, domain, output_context):
        """Create a basic output schema structure."""
        class OutputSchema:
            def __init__(self):
                self.type = "object"
                self.properties = {
                    "result": {
                        "type": "object",
                        "description": f"The output result: {output_context}",
                        "example": {"status": "success", "data": {}}
                    }
                }
            
            def model_dump(self):
                return {
                    "type": self.type,
                    "properties": self.properties
                }
        
        return OutputSchema()


def create_crew_with_flow(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """Creates a crew plan using the Multi-Crew Flow approach."""
    flow = MultiCrewFlow(user_task=user_task, config=config or {})
    result = flow.kickoff()
    
    # Result is the CrewPlan
    return result