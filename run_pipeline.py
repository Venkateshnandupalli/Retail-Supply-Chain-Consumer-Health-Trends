import subprocess
import sys
import os

def run_script(script_name):
    print(f"\n=========================================")
    print(f"[*] Running: {script_name}")
    print(f"=========================================")
    result = subprocess.run([sys.executable, script_name], capture_output=False, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {script_name} failed with return code {result.returncode}")
        sys.exit(result.returncode)
    print(f"[OK] {script_name} completed.")

def main():
    print("[START] Starting Retail Supply Chain Data Pipeline...")
    
    # 1. Run Data Prep (Simulation & Trend Injection)
    run_script("data_prep.py")
    
    # 2. Run Database Creator (Relational DB & SQL views builder)
    run_script("create_db.py")
    
    # 3. Run Analysis (Console SQL queries metrics)
    run_script("analysis.py")
    
    print("\n=========================================")
    print("[FINISHED] Pipeline Run Complete!")
    print("=========================================")
    print("Available Commands:")
    print("1. Standalone Charts:  python visualize.py")
    print("2. Web App Dashboard:  python -m streamlit run dashboard.py")
    print("=========================================\n")

if __name__ == "__main__":
    main()
