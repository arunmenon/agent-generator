# ui.py (example)
import gradio as gr
import requests

def submit_form(user_description, user_input_description, user_output_description, user_tools, user_process,
                user_planning, user_knowledge, user_human_input_tasks, user_memory, user_cache, user_manager_llm):
    payload = {
        "user_description": user_description,
        "user_input_description": user_input_description,
        "user_output_description": user_output_description,
        "user_tools": [t.strip() for t in user_tools.split(",") if t.strip()],
        "user_process": user_process,
        "user_planning": user_planning,
        "user_knowledge": user_knowledge,
        "user_human_input_tasks": user_human_input_tasks,
        "user_memory": user_memory,
        "user_cache": user_cache,
        "user_manager_llm": user_manager_llm if user_manager_llm.strip() else None
    }

    # POST these inputs to your API endpoint that runs the meta-crew
    response = requests.post("http://localhost:8000/meta-agent/create_crew", json=payload)
    return response.json()

with gr.Blocks() as demo:
    gr.Markdown("# Meta-Crew Configuration UI")
    user_description = gr.Textbox(label="Agent Goal")
    user_input_description = gr.Textbox(label="Input Description (e.g., 'A list of product names')")
    user_output_description = gr.Textbox(label="Output Description (e.g., 'A JSON taxonomy')")
    user_tools = gr.Textbox(label="Tools (comma-separated)", placeholder="e.g. WebSearchTool")
    user_process = gr.Radio(label="Process Type", choices=["sequential","hierarchical"], value="sequential")
    user_planning = gr.Checkbox(label="Enable Planning?", value=False)
    user_knowledge = gr.Checkbox(label="Use Knowledge Sources?", value=False)
    user_human_input_tasks = gr.Checkbox(label="Tasks require human input?", value=False)
    user_memory = gr.Checkbox(label="Enable Memory?", value=True)
    user_cache = gr.Checkbox(label="Enable Cache?", value=True)
    user_manager_llm = gr.Textbox(label="Manager LLM (if hierarchical)", placeholder="e.g. gpt-4")

    submit_button = gr.Button("Create Crew")
    output = gr.JSON()

    submit_button.click(
        fn=submit_form,
        inputs=[user_description, user_input_description, user_output_description, user_tools, user_process,
                user_planning, user_knowledge, user_human_input_tasks, user_memory, user_cache, user_manager_llm],
        outputs=output
    )

demo.launch()
