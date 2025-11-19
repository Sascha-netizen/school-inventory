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
        print(Fore.BLUE + Style.BRIGHT + "\n====Which school inventory would you like to access?====\n")
        print(Fore.YELLOW + "[1] Library")
        print(Fore.YELLOW + "[2] Supplies")
        print()

        while True:
            choice = input(Fore.GREEN + "\nEnter 1 or 2: ").strip()
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
        print(Fore.BLUE + Style.BRIGHT + "\n====You are now managing the Library====\n")
        print(Fore.YELLOW + "[1] Add book")
        print(Fore.YELLOW + "[2] Update existing book")
        print(Fore.YELLOW + "[3] Display book")
        print(Fore.YELLOW + "[4] Delete book")
        print(Fore.YELLOW + "[5] Exit / End of session")

        while True:
            choice = input(Fore.GREEN + "Enter a number of your choice [1-5]: ").strip()
            if choice == "1":
                self.add_book()
            elif choice == "2":
                print(Fore.MAGENTA + "\nUpdate existing book selected\n")
            elif choice == "3":
                print(Fore.MAGENTA + "\nDisplay existing book selected\n")
            elif choice == "4":
                print(Fore.MAGENTA + "\nDelete existing book selected\n")
            elif choice == "5":
                print(Fore.MAGENTA + "\nEnd of session. Returning to main menu\n")
                break
            else:
                print(Fore.RED + Style.BRIGHT + "\nInvalid choice. Please choose options [1] to [5]\n")

    def add_book(self):
        worksheet_library = self.sheet.worksheet("Library")
        print(Fore.CYAN + "\n=== Add a new book ===\n")
        book_id = input(Fore.GREEN + "Enter book ID: ").strip()
        title = input(Fore.GREEN + "Enter title: ").strip()
        author = input(Fore.GREEN + "Enter author: ").strip()
        quantity = input(Fore.GREEN + "Enter quantity: ").strip()
        category = input(Fore.GREEN + "Enter category: ").strip()
        notes = input(Fore.GREEN + "Enter notes: ").strip()

        worksheet_library.append_row([book_id, title, author, quantity, category, notes])
        print(Fore.MAGENTA + "\nBook added successfully.\n")



    def option_two_supplies(self):
        """
        Option two allows users to access and manage the records of the supplies department.
        """
        print(Fore.BLUE + Style.BRIGHT + "\n====You are now managing the Supplies====\n")
        print(Fore.YELLOW + "[1] Add item")
        print(Fore.YELLOW + "[2] Update existing item")
        print(Fore.YELLOW + "[3] Display item")
        print(Fore.YELLOW + "[4] Delete item")
        print(Fore.YELLOW + "[5] Exit / End of session")

        while True:
            choice = input(Fore.GREEN + "Enter a number of your choice [1-5]: ").strip()
            if choice == "1":
                print(Fore.MAGENTA + "\nAdd item selected\n")
            elif choice == "2":
                print(Fore.MAGENTA + "\nUpdate item selected\n")
            elif choice == "3":
                print(Fore.MAGENTA + "\nDisplay existing item selected\n")
            elif choice == "4":
                print(Fore.MAGENTA + "\nDelete existing item selected\n")
            elif choice == "5":
                print(Fore.MAGENTA + "\nEnd of session selected\n")
                break
            else:
                print(Fore.RED + Style.BRIGHT + "\nInvalid choice. Please choose options [1] to [5]\n")

        

if __name__ == "__main__":
    inventory_system = InventorySystem(SHEET)

    while True:
        selected_inventory = inventory_system.choose_inventory()
        print(Fore.MAGENTA + f"\nYou selected: {selected_inventory}")

        if selected_inventory == "Library":
            inventory_system.option_one_library()

        elif selected_inventory == "Supplies":
            inventory_system.option_two_supplies()


    