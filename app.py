import gradio as gr
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_ID = "google/gemini-2.0-flash-exp:free"

def generate_files(user_prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    few_shot_prompt = """
You are a CAD assistant that converts user instructions into two outputs:

1. A JSON file `params.json` describing the design parameters.
2. A Python script `fusion_script.py` using Fusion360 API to generate the requested shape.

Only return the code files. Start with:
###PARAMS.JSON
{...}
###FUSION_SCRIPT.PY
<python code here>
    """

    examples = """
Example:
User: "Make a cube 10x10x10"
Output:
###PARAMS.JSON
{
  "width": 10,
  "height": 10,
  "depth": 10
}
###FUSION_SCRIPT.PY
import adsk.core, adsk.fusion, adsk.cam, traceback
def run(context):
    try:
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        width = 10
        height = 10
        depth = 10
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(width, height, 0)
        )
        prof = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(depth)
        extInput.setDistanceExtent(False, distance)
        extrudes.add(extInput)
    except:
        app.userInterface.messageBox('Failed: {}'.format(traceback.format_exc()))
    """

    system_prompt = few_shot_prompt + examples

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    content = result['choices'][0]['message']['content']

    # Parse AI's output
    try:
        # Extract between markers
        param_start = content.find("###PARAMS.JSON") + len("###PARAMS.JSON")
        script_start = content.find("###FUSION_SCRIPT.PY")

        param_str = content[param_start:script_start].strip()
        script_str = content[script_start + len("###FUSION_SCRIPT.PY"):].strip()

        # Save param.json
        with open("params.json", "w") as f:
            f.write(param_str)

        # Save fusion_script.py
        with open("fusion_script.py", "w") as f:
            f.write(script_str)

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
