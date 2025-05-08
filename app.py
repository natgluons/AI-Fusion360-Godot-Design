import gradio as gr
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_ID = "google/gemini-2.0-flash-exp:free"

def generate_files(user_prompt):
    # Define your OpenRouter call
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are a CAD assistant. Based on the user's prompt, generate a params.json file "
        "with all key-value parameters needed for the design, and a Fusion360 Python script "
        "using these parameters. Only return plain JSON and Python script as separate sections."
    )
    
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    
    # Basic error handling
    try:
        # Use OpenRouter API to convert user_prompt into params
        # (mocked below for example)
        # In a real implementation, you would use the user_prompt to determine
        # the parameters for the CAD design.
        # For this example, we'll use a simple heuristic:
        if "cube" in user_prompt.lower():
            params = {"width": 25, "height": 25, "depth": 25}
        elif "rectangle" in user_prompt.lower():
            params = {"width": 40, "height": 20, "depth": 10}
        else:
            # Default parameters
            params = {"width": 30, "height": 30, "depth": 30}

        # Save JSON
        with open("params.json", "w") as f:
            json.dump(params, f, indent=4)

        # Load and use template for .py
        with open("template_fusion_script.py", "r") as f:
            with open("fusion_script.py", "w") as outfile:
                script_template = f.read()
                script_template = script_template.replace("WIDTH", str(params["width"]))
                script_template = script_template.replace("HEIGHT", str(params["height"]))
                script_template = script_template.replace("DEPTH", str(params["depth"]))
                outfile.write(script_template)

        return "Files generated successfully!", "params.json", "fusion_script.py"

    except Exception as e:
        return f"Parsing error: {e}", None, None

# Gradio UI
iface = gr.Interface(
    fn=generate_files,
    inputs=gr.Textbox(label="Enter Design Prompt", lines=4, placeholder="e.g., Make a rectangular block with 4 holes on top..."),
    outputs=[
        gr.Textbox(label="Status"),
        gr.File(label="Download params.json"),
        gr.File(label="Download fusion_script.py")
    ],
    title="Fusion360 CAD Generator"
)

if __name__ == "__main__":
    iface.launch()
