import os
import sys
import subprocess

def run_script(script_name):
    try:
        subprocess.run(["python", script_name])
    except Exception as e:
        print(f"An error occurred while running {script_name}: {e}")

def main():
    print("Select the script to run:")
    print("1. Data Preparation (DataPrep.py)")
    print("2. Feature Selection (FeatureSelection.py)")
    print("3. Model Builder (model_builder.py)")
    print("4. Logistic Regression Model (logReg_model.py)")
    print("5. DeBERTa Model (deBERTa_model.py)")
    print("6. Web Crawler (web_crawler.py)")
    print("7. Preprocessor (preprocessor.py)")

    choice = input("Enter the number corresponding to your choice: ")

    if choice == '1':
        run_script("DataPrep.py")
    elif choice == '2':
        run_script("FeatureSelection.py")
    elif choice == '3':
        run_script("model_builder.py")
    elif choice == '4':
        run_script("logReg_model.py")
    elif choice == '5':
        run_script("deBERTa_model.py")
    elif choice == '6':
        run_script("web_crawler.py")
    elif choice == '7':
        run_script("preprocessor.py")
    else:
        print("Invalid choice. Please run the script again and select a valid option.")

if __name__ == "__main__":
    main()
