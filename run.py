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
    

    def _search_record(self, worksheet, headers):
        """
        Generic search function for both library and supplies. Records are searchable by chosen columns (submenu).
        """
        rows = worksheet.get_all_values()
        if not rows:
            print(Fore.RED + "No records found in this sheet.")
            return
        
        data_headers = rows[0]
        data_rows = rows[1:]
    
        # Ask user which column to search
        if headers:
            print(Fore.BLUE + "\n=== Search Options ===\n")
            for i, h in enumerate(headers):
                print(Fore.YELLOW + f"[{i+1}] {h}")
            print(Fore.YELLOW + f"[{len(headers)+1}] View all records")

            while True:
                choice = input(Fore.GREEN + f"Choose an option [1-{len(headers)+1}]: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(headers)+1:
                    choice = int(choice)
                    break
                else: 
                    print(Fore.RED + "Invalid choice. Try again!")
                
            # View entire record
            if choice == len(headers)+1:
                results = data_rows
            else:
                col_index = choice -1
                keyword = input(Fore.GREEN + f"Enter keyword for {headers[col_index]}: ").strip().lower()
                results = [row for row in data_rows if keyword in row[col_index].lower()]
        
        else: 
            # if no headers provided, display entire record
            results = data_rows
        
        if not results:
            print(Fore.RED + "No matching records found.")
            return
        
        print(Fore.YELLOW + "\n===Search results===")
        print(Fore.CYAN + " | ".join(data_headers))
        print(Fore.CYAN + "-"*60)
        for row in results:
            print(Fore.MAGENTA + " | ".join(row))
        print()    


    def option_one_library(self):
        """
        Option one allows users to access and manage the library records.
        """
        print(Fore.BLUE + Style.BRIGHT + "\n====You are now managing the Library====\n")
        print(Fore.YELLOW + "[1] Add book")
        print(Fore.YELLOW + "[2] Update existing book")
        print(Fore.YELLOW + "[3] Search or display book")
        print(Fore.YELLOW + "[4] Delete book")
        print(Fore.YELLOW + "[5] Exit / End of session")

        while True:
            choice = input(Fore.GREEN + "Enter a number of your choice [1-5]: ").strip()
            if choice == "1":
                self.add_book()
            elif choice == "2":
                self.update_book()
            elif choice == "3":
                self.search_book()
            elif choice == "4":
                self.delete_book()
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


    def search_book(self):
        """
        Search or display library records.
        """
        library_headers = ["ID", "Title", "Author", "Quantity", "Category", "Notes"]
        self._search_record(self.sheet.worksheet("Library"), library_headers)
    

    def delete_book(self):
        """
        Delete a book from the library by its ID.
        """
        worksheet_library = self.sheet.worksheet("Library")
        book_id = input(Fore.GREEN + "Enter the book ID to delete (e.g., LIB-0001, q to cancel): ").strip()

        if book_id.lower() in ("q", "quit", "cancel"):
            print(Fore.MAGENTA + "Delete operation cancelled.")
            return
        
        try:
            cell = worksheet_library.find(book_id)
        except gspread.exceptions.CellNotFound:
            print(Fore.RED + "Book ID not found.")
            return
        
        confirm = input(Fore.YELLOW + f"Are you sure you want to delete book {book_id}? (y/n): ").strip().lower()
        if confirm == "y":
            worksheet_library.delete_rows(cell.row)
            print(Fore.MAGENTA + f"Book {book_id} deleted successfully.")
        else:
            print(Fore.MAGENTA + "Delete operation cancelled.")



    # The second part of the inventory system starts here:
    def option_two_supplies(self):
        """
        Option two allows users to access and manage the records of the supplies department.
        """
        print(Fore.BLUE + Style.BRIGHT + "\n====You are now managing the Supplies====\n")
        print(Fore.YELLOW + "[1] Add item")
        print(Fore.YELLOW + "[2] Update existing item")
        print(Fore.YELLOW + "[3] Search or display item")
        print(Fore.YELLOW + "[4] Delete item")
        print(Fore.YELLOW + "[5] Exit / End of session")

        while True:
            choice = input(Fore.GREEN + "Enter a number of your choice [1-5]: ").strip()
            if choice == "1":
                self.add_item()
            elif choice == "2":
                self.update_item()
            elif choice == "3":
                self.search_item()
            elif choice == "4":
                self.delete_item()
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
    
    def update_item(self):
        """
        Update existing supplies records.
        """
        worksheet_supplies = self.sheet.worksheet("Supplies")
        print(Fore.CYAN + "\n=== Update an existing item ===\n")

        product_id = input(Fore.GREEN + "Enter the Item ID to update (e.g., SUP-0001): ").strip()
        try:
            cell = worksheet_supplies.find(product_id)
        except gspread.exceptions.CellNotFound:
            print(Fore.RED + "Item ID not found.")
            return

        row_index = cell.row
        row_values = worksheet_supplies.row_values(row_index)

        print(Fore.YELLOW + "\nCurrent Values (press ENTER to leave unchanged):")
        fields = ["ID", "Product", "Brand", "Quantity", "Category", "Notes"]

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
        worksheet_supplies.update(f"A{row_index}:F{row_index}", [updated_values])
        print(Fore.MAGENTA + "\nItem updated successfully.")


    def search_item(self):
        """
        Search or display supplies records.
        """
        supplies_headers = ["ID", "Product", "Brand", "Quantity", "Category", "Notes"]
        self._search_record(self.sheet.worksheet("Supplies"), supplies_headers)
    


    def delete_item(self):
        """
        Delete an item from the supplies worksheet by its ID.
        """
        worksheet_supplies = self.sheet.worksheet("Supplies")
        item_id = input(Fore.GREEN + "Enter the Item ID to delete (e.g., SUP-0001, q to cancel): ").strip()

        if item_id.lower() in ("q", "quit", "cancel"):
            print(Fore.MAGENTA + "Delete operation cancelled.")
            return
        
        try:
            cell = worksheet_supplies.find(item_id)
        except gspread.exceptions.CellNotFound:
            print(Fore.RED + "Item ID not found.")
            return
        
        confirm = input(Fore.YELLOW + f"Are you sure you want to delete item {item_id}? (y/n): ").strip().lower()
        if confirm == "y":
            worksheet_supplies.delete_rows(cell.row)
            print(Fore.MAGENTA + f"Item {item_id} deleted successfully.")
        else:
            print(Fore.MAGENTA + "Delete operation cancelled.")




if __name__ == "__main__":
    inventory_system = InventorySystem(SHEET)

    while True:
        selected_inventory = inventory_system.choose_inventory()
        print(Fore.MAGENTA + f"\nYou selected: {selected_inventory}")

        if selected_inventory == "Library":
            inventory_system.option_one_library()

        elif selected_inventory == "Supplies":
            inventory_system.option_two_supplies()