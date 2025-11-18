import gspread
from google.oauth2.service_account import Credentials
from colorama import Fore, Style, init

init(autoreset=True)

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("school_inventory_system")


class InventorySystem:
    """
    Allows the user to choose which inventory subsystem - library or supplies - to enter
    """
    def __init__(self, sheet):
        self.sheet = sheet
    
    def choose_inventory(self):
        print(Fore.BLUE + Style.BRIGHT + "Which inventory would you like to access?")
        print(Fore.YELLOW + "[1] Library")
        print(Fore.YELLOW + "[2] Supplies")

        while True:
            choice = input(Fore.GREEN + "Enter 1 or 2: ").strip()
            if choice == "1":
                return "Library"
            elif choice == "2":
                return "Supplies"
            
            else:
                print(Fore.RED + Style.BRIGHT + "Your choice is invalid. Please choose 1 or 2.") 

if __name__ == "__main__":
    inventory_system = InventorySystem(SHEET)
    selected_inventory = inventory_system.choose_inventory()
    print(Fore.MAGENTA + f"You selected: {selected_inventory}")
    