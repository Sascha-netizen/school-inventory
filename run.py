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
                self.update_book()
            elif choice == "3":
                print(Fore.MAGENTA + "\nDisplay existing book selected\n")
            elif choice == "4":
                print(Fore.MAGENTA + "\nDelete existing book selected\n")
            elif choice == "5":
                print(Fore.MAGENTA + "\nEnd of session. Returning to main menu\n")
                break
            else:
                print(Fore.RED + Style.BRIGHT + "\nInvalid choice. Please choose options [1] to [5]\n")

    def _generate_suggested_id(self, prefix: str, worksheet):
            """
            Suggest the next available ID based on existing IDs, filling gaps if possible.
            """
            try:
                existing_ids = worksheet.col_values(1)
            except Exception:
                existing_ids = []

            # Extract numeric suffixes
            numbers = sorted(
                int(entry[len(prefix):]) for entry in existing_ids
                if entry.startswith(prefix) and entry[len(prefix):].isdigit()
            )

            # Find the smallest missing number in the sequence
            next_num = 1
            for num in numbers:
                if num == next_num:
                    next_num += 1
                elif num > next_num:
                    break  # found a gap

            return f"{prefix}{next_num:04d}"

    
    def _ask_for_id_with_suggestion(self, prefix: str, worksheet):
        """
        Show suggested ID, allow override, validate input, and prevent duplicates.
        """
        import re
        suggestion = self._generate_suggested_id(prefix, worksheet)
        pattern = re.compile(rf"^{re.escape(prefix)}\d{{4}}$")

        while True:
            print(Fore.YELLOW + f"Suggested ID: {suggestion}")
            user_input = input(
                Fore.GREEN + "Press Enter to accept or type a custom ID (q to cancel): "
            ).strip()

            if user_input == "":
                chosen_id = suggestion

            elif user_input.lower() in ("q", "quit", "cancel"):
                print(Fore.MAGENTA + "Operation cancelled.")
                return None

            else:
                chosen_id = user_input
                if not pattern.match(chosen_id):
                    print(Fore.RED + f"ID must match format {prefix}#### (e.g. {prefix}0001)")
                    continue

            existing_ids = worksheet.col_values(1)
            if chosen_id in existing_ids:
                print(Fore.RED + "This ID already exists. Choose another.")
                continue

            return chosen_id   


    def add_book(self):
        """
        Adds a new book to the existing library records.
        """
        worksheet_library = self.sheet.worksheet("Library")
        print(Fore.CYAN + "\n=== Add a new book ===\n")

        # Use ID suggestion system
        book_id = self._ask_for_id_with_suggestion("LIB-", worksheet_library)
        if book_id is None:  
            return

        title = input(Fore.GREEN + "Enter title: ").strip()
        author = input(Fore.GREEN + "Enter author: ").strip()

        # Quantity validation
        while True:
            quantity_input = input(Fore.GREEN + "Enter Quantity: ").strip()
            try:
                quantity = int(quantity_input)
                if quantity < 0:
                    print(Fore.RED + "Quantity cannot be negative. Try again.")
                    continue
                break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a numeric value.")

        category = input(Fore.GREEN + "Enter category: ").strip()
        notes = input(Fore.GREEN + "Enter notes: ").strip()

        worksheet_library.append_row([
            book_id,
            title,
            author,
            str(quantity),
            category,
            notes
        ])

        print(Fore.MAGENTA + "\nBook added successfully.\n")
    

    def update_book(self):
        """
        Update existing library records.
        """
        worksheet_library = self.sheet.worksheet("Library")
        print(Fore.CYAN + "\n=== Update an existing book ===\n")

        book_id = input(Fore.GREEN + "Enter the Book ID to update (e.g., LIB-0001): ").strip()
        try:
            cell = worksheet_library.find(book_id)
        except gspread.exceptions.CellNotFound:
            print(Fore.RED + "Book ID not found.")
            return

        row_index = cell.row
        row_values = worksheet_library.row_values(row_index)

        print(Fore.YELLOW + "\nCurrent Values (press ENTER to leave unchanged):")
        fields = ["ID", "Title", "Author", "Quantity", "Category", "Notes"]

        updated_values = []
        for i, field in enumerate(fields):
            # Always keep ID unchanged
            if field == "ID":
                updated_values.append(row_values[i])
                continue

            current = row_values[i] if i < len(row_values) else ""
            new_value = input(Fore.GREEN + f"{field} [{current}]: ").strip()

            if new_value == "":
                updated_values.append(current)
            else:
                if field == "Quantity":
                    while True:
                        try:
                            qty = int(new_value)
                            if qty < 0:
                                raise ValueError
                            updated_values.append(str(qty))
                            break
                        except ValueError:
                            new_value = input(Fore.RED + "Quantity must be a non-negative integer. Try again: ").strip()
                else:
                    updated_values.append(new_value)

        # Update the row in the sheet
        worksheet_library.update(f"A{row_index}:F{row_index}", [updated_values])
        print(Fore.MAGENTA + "\nBook updated successfully.")





    # The second part of the inventory system starts here:
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
                self.add_item()
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

    def add_item(self):
        """
        Add a new supplies item to the Supplies worksheet with automatic ID suggestion.
        """
        worksheet_supplies = self.sheet.worksheet("Supplies")
        print(Fore.CYAN + "\n=== Add a new supplies item ===\n")

        # Use ID suggestion system with SUP- prefix
        product_id = self._ask_for_id_with_suggestion("SUP-", worksheet_supplies)
        if product_id is None:  
            return

        # Collect input from user
        product = input(Fore.GREEN + "Enter product: ").strip()
        brand = input(Fore.GREEN + "Enter brand: ").strip()

        # Quantity validation
        while True:
            quantity_input = input(Fore.GREEN + "Enter Quantity: ").strip()
            try:
                quantity = int(quantity_input)
                if quantity < 0:
                    print(Fore.RED + "Quantity cannot be negative. Try again.")
                    continue
                break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a numeric value.")

        category = input(Fore.GREEN + "Enter category: ").strip()
        notes = input(Fore.GREEN + "Enter notes: ").strip()

        # Append new row to the worksheet
        worksheet_supplies.append_row([
            product_id,
            product,
            brand,
            str(quantity),
            category,
            notes
        ])

        print(Fore.MAGENTA + "\nItem added successfully.\n")


if __name__ == "__main__":
    inventory_system = InventorySystem(SHEET)

    while True:
        selected_inventory = inventory_system.choose_inventory()
        print(Fore.MAGENTA + f"\nYou selected: {selected_inventory}")

        if selected_inventory == "Library":
            inventory_system.option_one_library()

        elif selected_inventory == "Supplies":
            inventory_system.option_two_supplies()
