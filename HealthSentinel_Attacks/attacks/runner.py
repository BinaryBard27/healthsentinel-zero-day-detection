import os
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        print("==========================================")
        print("   HEALTH SENTINEL: RED TEAM ATTACK MENU  ")
        print("==========================================")
        print("1. SQL Injection (Database Breach)")
        print("2. Phishing Simulation (Suspicious URL)")
        print("3. Ransomware Simulation (File Encryption)")
        print("4. Insider Threat (Bulk Data Access)")
        print("5. Exit")
        print("------------------------------------------")
        
        choice = input("Select an attack to launch [1-5]: ")
        base_path = os.path.dirname(os.path.abspath(__file__))

        if choice == '1':
            subprocess.run(["python", os.path.join(base_path, "sqli_attack.py")])
        elif choice == '2':
            subprocess.run(["python", os.path.join(base_path, "phishing_link.py")])
        elif choice == '3':
            subprocess.run(["python", os.path.join(base_path, "ransom_sim.py")])
        elif choice == '4':
            subprocess.run(["python", os.path.join(base_path, "insider_threat.py")])
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid selection.")
        
        input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()