# text-to-CAD model performance
Feature:
- Few Shot Learning
- Examples in Separated Files

```
Test Case 1: Create a table
Test Case 2: Build a 50 mm tall cone with 25 mm base diameter, and place a torus ring (15 mm inner diameter, 5 mm thickness) halfway up the cone, centered
```

1. Model: deepseek/deepseek-chat-v3-0324:free
Test Case 1: upside down table (40-50s)
Test Case 2: Unclosed profile (script generated successfully, but cannot generate .obj file in Fusion360)

2. Model: deepseek/deepseek-r1:free
Test Case 1: upside down table (~60s)
Test Case 2: Error: Response format invalid - missing required sections (stuck in reasoning, stopped/uncomplete reasoning even when max token not set)

3. Model: google/gemini-2.0-flash-exp:free
Test Case 1: (Files generated in 6.83s). RuntimeError: 3 : invalid argument inputEntities, error in entities.add(leg), should be entities.add(leg.bodies.item(0))
Tase Case 2: skipped

4. Model: meta-llama/llama-4-maverick:free
Test Case 1: (Files generated in 29.12s). upside down table
Test Case 2: (Files generated in 27.21s).  isn't generating two enclosed profiles

5. Model: qwen/qwen3-235b-a22b:free
Test Case 1: ERROR:__main__:Error (line 179): 'choices'
Test Case 2: skipped