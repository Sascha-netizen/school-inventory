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
        """
        Displays main inventory options and allows user to choose between either library or supplies.
        """
        print(Fore.BLUE + Style.BRIGHT + "\nWhich inventory would you like to access?\n")
        print(Fore.YELLOW + "[1] Library")
        print(Fore.YELLOW + "[2] Supplies")
        print()

        while True:
            choice = input(Fore.GREEN + "Enter 1 or 2: ").strip()
            if choice == "1":
                return "Library"
            elif choice == "2":
                return "Supplies"
            
            else:
                print(Fore.RED + Style.BRIGHT + "\nYour choice is invalid. Please choose 1 or 2.\n") 

    def option_one_library(self):
        """
        Option one allows users to access and manage the library records.
        """
        print(f"\nYou are now managing the Library\n")
        print("[1] Add book")
        print("[2] Update existing book")
        print("[3] Display book")
        print("[4] Delete book")
        print("[5] Exit / End of session")

        while True:
            choice = input("Select an option [1-5]: ").strip()
            if choice == "1":
                print("Add book selected")
            elif choice == "2":
                print("Update existing book selected")
            elif choice == "3":
                print("Display existing book selected")
            elif choice == "4":
                print("Delete existing book selected")
            elif choice == "5":
                print("End of session selected")
                break
            else:
                print("Invalid choice. Please choose options [1] to [5]")


    def option_two_supplies(self):
        """
        Option two allows users to access and manage the records of the supplies department.
        """
        print(f"\nYou are now managing the Supplies\n")
        print("[1] Add item")
        print("[2] Update existing item")
        print("[3] Display item")
        print("[4] Delete item")
        print("[5] Exit / End of session")

        while True:
            choice = input("Select an option [1-5]: ").strip()
            if choice == "1":
                print("Add item selected")
            elif choice == "2":
                print("Update item selected")
            elif choice == "3":
                print("Display existing item selected")
            elif choice == "4":
                print("Delete existing item selected")
            elif choice == "5":
                print("End of session selected")
                break
            else:
                print("Invalid choice. Please choose options [1] to [5]")

        

if __name__ == "__main__":
    inventory_system = InventorySystem(SHEET)

    while True:
        selected_inventory = inventory_system.choose_inventory()
        print(Fore.MAGENTA + f"\nYou selected: {selected_inventory}")

        if selected_inventory == "Library":
            inventory_system.option_one_library()

        elif selected_inventory == "Supplies":
            inventory_system.option_two_supplies()


    