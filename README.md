# AgentCreator Crew

Welcome to the AgentCreator Crew project, powered by [crewAI](https://crewai.com). This project provides tools for generating CrewAI crews based on user-defined tasks using a hierarchical, multi-crew approach.

## Architecture Overview

The Agent Creator uses a hierarchical flow architecture with four specialized crews:

1. **Analysis Crew**: Analyzes requirements, determines complexity and process type
2. **Planning Crew**: Selects algorithms (Best-of-N, Tree-of-Thoughts, REBASE) for planning
3. **Implementation Crew**: Defines agents, tasks, and workflow
4. **Evaluation Crew**: Scores and suggests improvements

Each crew contributes to an iterative refinement process that results in a fully specified CrewAI configuration.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/agent_creator/config/agents.yaml` to define your agents
- Modify `src/agent_creator/config/tasks.yaml` to define your tasks
- Modify `src/agent_creator/crew.py` to add your own logic, tools and specific args
- Modify `src/agent_creator/main.py` to add custom inputs for your agents and tasks

## Flow Architecture

The flow architecture orchestrates the specialized crews in a sequential process with feedback loops:

```
Analysis → Planning → Implementation → Evaluation → Final Crew Plan
    ↑          ↑            ↑               |
    └──────────┴────────────┴───────────────┘
             (Refinement Loop)
```

- The process starts with analysis of the user's task
- Each crew builds on the output of previous crews
- Evaluation determines if refinement is needed
- Refinement loops target specific areas for improvement

## API Usage

### REST API

The API provides endpoints for creating crews using the flow approach:

- `POST /flow/create`: Create a new crew with the flow approach
- `POST /flow/debug`: Debug endpoint that returns intermediate results

### Direct Usage

You can also use the flow directly in your code:

```python
from src.agent_creator.flow_crew import create_crew_with_flow

# Create a new crew plan
crew_plan = create_crew_with_flow(
    user_task="Design a research assistant that helps collect and summarize scientific papers",
    config={"model_name": "gpt-4o", "temperature": 0.7}
)

# Access the agents and tasks
for agent in crew_plan.agents:
    print(f"Agent: {agent.name}, Role: {agent.role}")

for task in crew_plan.tasks:
    print(f"Task: {task.name}, Purpose: {task.purpose}")
```

## CLI Usage for Flow

Run the flow directly from the command line:

```bash
# Run directly (no API)
python -m src.agent_creator.main flow --task "Design a customer support chatbot that can handle product inquiries"

# Run via API
python -m src.agent_creator.main flow --api --task "Design a customer support chatbot"

# Run with debug information
python -m src.agent_creator.main flow --api --debug --task "Design a customer support chatbot"
```

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the agent-creator Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The agent-creator Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the AgentCreator Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
