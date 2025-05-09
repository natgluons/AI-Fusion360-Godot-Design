import json
import argparse
import os
import logging
import time
import gradio as gr
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_ID = "deepseek/deepseek-r1:free"
system_prompt =  {
            "role": "system", 
            "content": """You are a CAD assistant that converts user instructions into a JSON parameters file and a Python script for Fusion 360. 
            Your response MUST contain exactly two sections:
            1. ### PARAMS.JSON - A JSON object with all parameters needed for the design
            2. ### FUSION_SCRIPT.PY - A complete Python script that implements the design in Fusion 360
            
            The JSON and Python code must be properly formatted and executable. Ensure the file names are correct and the code is valid.
            Do not include any other text, formatting, or explanations."""
        }

def read_example_file(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
            logger.error(f"Error reading file {file_path} (line {e.__traceback__.tb_lineno}): {str(e)}")
            return None

def get_example_messages() -> list:
    examples = []
    
    # Example 1
    example1_params = read_example_file('example1_params.json')
    example1_script = read_example_file('example1_script.py')
    if example1_params and example1_script:
        examples.append(system_prompt)
        examples.append({
            "role": "user",
            "content": "Make a cube 10x10x10"
        })
        examples.append({
            "role": "assistant",
            "content": f"### PARAMS.JSON\n{example1_params}\n### FUSION_SCRIPT.PY\n{example1_script}"
        })

    # Example 2
    example2_params = read_example_file('example2_params.json')
    example2_script = read_example_file('example2_script.py')
    if example2_params and example2_script:
        examples.append(system_prompt)
        examples.append({
            "role": "user",
            "content": "Create cylinder with sphere on top"
        })
        examples.append({
            "role": "assistant",
            "content": f"### PARAMS.JSON\n{example2_params}\n### FUSION_SCRIPT.PY\n{example2_script}"
        })

    # Example 3
    example3_params = read_example_file('example3_params.json')
    example3_script = read_example_file('example3_script.py')
    if example3_params and example3_script:
        examples.append(system_prompt)
        examples.append({
            "role": "user",
            "content": "Make rectangular block with holes"
        })
        examples.append({
            "role": "assistant",
            "content": f"### PARAMS.JSON\n{example3_params}\n### FUSION_SCRIPT.PY\n{example3_script}"
        })

    return examples

def generate_file(user_prompt, example_number=1):
    # Parse example number from command line
    parser = argparse.ArgumentParser(description='Generate CAD files from examples')
    parser.add_argument('--example', type=int, default=example_number,
                        choices=[1, 2, 3],
                        help='Select which example to run (1-3)')
    args = parser.parse_args()
    
    # Load only the selected example
    if args.example == 1:
        example_params = read_example_file('example1_params.json')
        example_script = read_example_file('example1_script.py')
    elif args.example == 2:
        example_params = read_example_file('example2_params.json')
        example_script = read_example_file('example2_script.py')
    elif args.example == 3:
        example_params = read_example_file('example3_params.json')
        example_script = read_example_file('example3_script.py')
    else:
        logger.error("Invalid example number")
        return "Invalid example number", None, None

    # API key handling with check
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:7863",
        "Host": "openrouter.ai",
    }

    messages = []
    messages.extend(get_example_messages())
    messages.extend([
        system_prompt,
        {
            "role": "user",
            "content": user_prompt
        }
    ])

    # save request to file
    with open("request.json", "w") as f:
        json.dump(messages, f, indent=2)

    payload = {
        "model": "anthropic/claude-3-opus",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000,
        "stop_sequences": ["\n\nHuman:"]
    }

    # logger.info(f"Payload being sent to OpenRouter: {json.dumps(payload)}")

    try:
        start_time = time.time()
        with tqdm(total=100, desc="Generating CAD file") as pbar:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            pbar.update(30)
            try:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            except requests.exceptions.HTTPError as e:
                try:
                    error_message = response.json().get("error", {}).get("message", str(e))
                except json.JSONDecodeError:
                    error_message = str(e)
                logger.error(f"HTTP error (line {e.__traceback__.tb_lineno}): {error_message}")
                return f"Error: {error_message}", None, None
            pbar.update(40)
            result = response.json()
            pbar.update(30)

        # save response to file
        with open("response.json", "w") as f:
            json.dump(result, f, indent=2)

        content = result["choices"][0]["message"]["content"]

        try:
            # More robust parsing that handles variations in the format
            if "### PARAMS.JSON" in content:
                params_content = content.split("### PARAMS.JSON")[1].split("### FUSION_SCRIPT.PY")[0].strip()
            elif "###PARAMS.JSON" in content:
                params_content = content.split("###PARAMS.JSON")[1].split("###FUSION_SCRIPT.PY")[0].strip()
            else:
                raise ValueError("Response format invalid - missing required sections")
            if "### FUSION_SCRIPT.PY" in content:
                script_content = content.split("### FUSION_SCRIPT.PY")[1].strip()
            elif "###FUSION_SCRIPT.PY" in content:
                script_content = content.split("###FUSION_SCRIPT.PY")[1].strip()
            else:
                raise ValueError("Response format invalid - missing required sections")

            with open("params.json", "w") as f:
                json.dump(json.loads(params_content), f, indent=2)

            with open("fusion_script.py", "w") as f:
                f.write(script_content)

            return f"Files generated in {time.time() - start_time:.2f}s", "params.json", "fusion_script.py"

        except IndexError as e:
            logger.error(f"Error parsing response content (line {e.__traceback__.tb_lineno}): {str(e)}")
            return f"Error: Could not parse response from OpenRouter. Please try again.", None, None

    except Exception as e:
        logger.error(f"Error (line {e.__traceback__.tb_lineno}): {str(e)}")
        return f"Error: {str(e)}", None, None

if __name__ == "__main__":
    iface = gr.Interface(
        fn=generate_file,
        inputs=gr.Textbox(label="Enter CAD instructions", lines=4),
        outputs=[
            gr.Textbox(label="Status"),
            gr.File(label="Download params.json"),
            gr.File(label="Download script")
        ],
        title="Fusion 360 CAD Generator"
    )
    iface.launch()
