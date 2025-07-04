# What Is This Project?
This project explores AI generative design for game development, where natural language instructions are used to script 3D designs in Fusion 360, simulate their behavior in Godot, and tune them using Bayesian optimization to automate and accelerate game-relevant mechanical design without requiring expert CAD skills.

This combines:
* Generative CAD scripting (Fusion 360)
* Text-to-design using LLMs (NLP)
* Physics-based simulation (Godot)
* Bayesian optimization for AI tuning (scikit-optimize)

# Why It Matters
Creating 3D mechanical models for game prototypes or simulations often requires deep CAD knowledge and manual tweaking. This project makes it more accessible by:
- Letting non-technical users describe designs in plain text (e.g. "make a low-profile four-wheeled robot with large front wheels")
- Using LLMs to generate Fusion 360 Python scripts from that text
- Automating the simulation process in Godot
- Tuning parameters automatically using Bayesian optimization

# Text-to-CAD with NLP
I use an LLM (DeepSeek-Coder) to convert structured English prompts into Fusion 360 scripts. These scripts define parameterized 3D components (e.g. a robot base, linkages, wheels) using Fusion’s Python API. This lowers the barrier for CAD modeling and makes the workflow more game-dev friendly.

How to run this pipeline interactively:

```
Prompt: "Create a long rectangular chassis with four wheels, and a rotating front sensor mount"
→
LLM: Outputs Python script using Fusion API
→
Fusion 360: Builds the CAD model
```

# Game-Oriented Design and Testing
Each generated model can be exported as .obj and imported into Godot for testing in a physics simulation (e.g. pushing a robot across a surface to test distance, torque, or balance).

This allows game devs or simulation designers to:
- Rapidly test different mechanical configurations
- Evaluate how design changes affect in-game performance
- Visualize and debug in a familiar game engine

# AI Optimization Loop
I implement Bayesian optimization (via scikit-optimize) to iteratively search for better designs by:
- Sampling design parameters (e.g. chassis width, wheel size)
- Generating the design in Fusion
- Simulating in Godot
- Scoring performance (e.g., distance traveled)
- Using the score to guide the next iteration

# Summary
1. Text-to-CAD	LLM for code generation using DeepSeek-Coder
2. Design optimization	Black-box tuning	Bayesian optimizer (scikit-optimize)
3. Simulation & evaluation	Physics engine	Godot (automated scoring)

# Planned Next Development
- Design Reward-based learning from performance	RL / Metaheuristics 