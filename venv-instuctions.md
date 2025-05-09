# 1. Open PowerShell
# 2. Navigate to your project folder:
cd C:\Files\Personal\AI-Fusion360-Godot-Design
# 3. Temporarily allow script execution:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# 4. Activate the virtual environment:
.\gradioenv\Scripts\Activate.ps1
# 5. Install required packages: 
pip install -r requirements.txt
# 6. Run your app: 
python app.py
