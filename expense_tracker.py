import json
import os

# Setting the location for the data file:

current_file_path = __file__
absolute_current_file_path = os.path.abspath(current_file_path)
current_directory_path = os.path.dirname(absolute_current_file_path)
data_file_path = os.path.join(current_directory_path, "data.json")

NUM_OF_OPTIONS = 10


# Class that stores and handles data:

class Storage:

    def __init__(self, data_file_path, username, currency):
        self.data_file_path = data_file_path

        # User-related-data:
        self.username = username
        self.currency = currency

        # Expenses-related-data
        self.expenses = []
        self.categories = []

    def load_data(self):
        try:
            with open(self.data_file_path, "r") as f:
                data = json.load(f)
                safe_user_data = self.validate_user_related_data(data)
                safe_expenses_data = self.validate_expenses_related_data(data)

                if safe_user_data and safe_expenses_data:
                    return True, True

                elif safe_user_data and not safe_expenses_data:
                    return True, False

                return False, False
            
        except (KeyError, json.JSONDecodeError):
            return None, None

        except (FileNotFoundError):
            return False, False

    def validate_user_related_data(self, data):
        temp_username = data["user_related_data"]["username"]
        temp_currency = data["user_related_data"]["currency"]

        if temp_username.strip() and temp_currency.strip():
            self.username = temp_username
            self.currency = temp_currency
            return True

        return False

    def validate_expenses_related_data(self, data):
        temp_expenses = data["expenses_related_data"]["expenses"]
        temp_categories = data["expenses_related_data"]["categories"]

        expenses_are_valid = self.validate_expenses(temp_expenses)
        categories_are_valid = self.validate_categories(temp_categories)

        if expenses_are_valid and categories_are_valid:
            self.expenses = temp_expenses
            self.categories = temp_categories

            return True

        return False

    def validate_expenses(self, expenses):
        if type(expenses) is not list:
            return False

        for expense in expenses:
            if type(expense) is not dict:
                return False

            if expense.get("name")is None or expense.get("cost") is None:
                return False

            if type(expense["name"]) is not str:
                return False

            if type(expense["cost"]) is not int and type(expense["cost"]) is not float:
                return False

        return True 

    def validate_categories(self, categories):
        if type(categories) is not list:
            return False

        for category in categories:
            if type(category) is not dict:
                return False

            if category.get("name") is None:
                return False

            if type(category["name"]) is not str:
                return False
            
            if category.get("expenses") is None:
                return False

            expenses_are_valid = self.validate_expenses(category["expenses"])

            if not expenses_are_valid:
                return False

        return True

    # 1. Storing Expense:
    def store_expense(self, expense_name, expense_cost):
        expense = {"name": expense_name, "cost": expense_cost}
        self.expenses.append(expense)

    def does_expense_name_already_exist(self, target_expense_name):
        for expense in self.expenses:
            if expense["name"] == target_expense_name:
                return True, False, expense
        return self.is_expense_already_categorized(target_expense_name)

    # 2. Storing Category:
    def store_category(self, category_name):
        self.categories.append({"name": category_name, "expenses": []})

    def does_category_name_already_exist(self, target_expense_name):
        for category in self.categories:
            if category["name"] == target_expense_name:
                return True
        return False

    # 3. Storing Expense into Category:
    def store_expense_into_category(self, expense, category):
        category["expenses"].append(expense)

    def is_expense_already_categorized(self, target_expense_name):
        for category in self.categories:
            for expense in category["expenses"]:
                if expense["name"] == target_expense_name:
                    return True, True, category
        return False, False, None

    # 4. Showing Expenses:
    def has_expenses_in_categories(self):
        for category in self.categories:
            if category["expenses"]:
                return True
        return False

    def has_expenses(self):
        if self.expenses:
            return True
        for category in self.categories:
            if category["expenses"]:
                return True
        return False

    def get_category_total_cost(self, category):
        total_category_cost = 0
        for expense in category["expenses"]:
            total_category_cost += expense["cost"]
        return total_category_cost

    def calculate_total_cost(self):
        total_cost = 0
        for category in self.categories:
            for expense in category["expenses"]:
                total_cost += expense["cost"]

        for expense in self.expenses:
            total_cost += expense["cost"]

        return total_cost

    # 6. Removing Expenses:
    def locate_expense(self, target_expense_name):
        for expense in self.expenses:
            if expense["name"] == target_expense_name:
                return True, expense, self.expenses

        for category in self.categories:
            for expense in category["expenses"]:
                if expense["name"] == target_expense_name:
                    return True, expense, category

        return False, None, None

    def remove_expense(self, target_expense, location):
        # If the expense has to be removed from the general expenses list:
        if location == self.expenses:
            self.expenses.remove(target_expense)
            return

        # If the expense has to be removed from a category:
        location["expenses"].remove(target_expense)

    # 7. Removing Categories:
    def has_categories(self):
        if self.categories:
            return True
        return False

    def category_already_exists(self, target_category_name):
        for category in self.categories:
            if category["name"] == target_category_name:
                return True, category
        return False, None

    def category_has_expenses(self, category):
        if category["expenses"]:
            return True
        return False

    def move_expenses_out_of_category(self, category):
        self.expenses.extend(category["expenses"])

    def remove_category(self, category):
        self.categories.remove(category)

    # 10. Saving Data:

    def save_data(self):
        with open(self.data_file_path, "w") as f:
            data = {
                "user_related_data": {
                    "username": self.username,
                    "currency": self.currency,
                },
                "expenses_related_data": {
                    "expenses": self.expenses,
                    "categories": self.categories,
                },
            }
            json.dump(data, f)


# Class that handles UI and orchestrates the app:


class ExpenseTracker:

    def __init__(self):
        self.storage = Storage(data_file_path, None, None)

    def run(self):
        self.introduction()
        while True:
            user_choice = self.get_user_choice()
            self.execute_user_choice(user_choice)
            if user_choice == 10:
                break
            self.print_options()

    def introduction(self):
        user_data, expenses_data = self.storage.load_data()

        # What happens if the data file is corrupted:
        if user_data is None and expenses_data is None:
            print("we are sorry to inform you that an unexpected problem accured while loading your data, and as a result, we have to reset your information entirely.")
            self.storage.username, self.storage.currency = self.first_time_setup()
            self.print_options()
            print(
                "\njust make sure that before you close the app: select '10', to save all your data!"
            )

        elif user_data and not expenses_data:
            print(f"{self.storage.username}, we are sorry to inform you that an unexpected problem accured while loading your data and your expenses have been lost.")
            self.print_options()

        # What happens if it's the user's first time logging in:
        elif not user_data:
            print("hey there! welcome to Denis's expense tracker!")

            self.storage.username, self.storage.currency = self.first_time_setup()

            print(
                f"\nperfect {self.storage.username}, now that I saved your currency as '{self.storage.currency}' we're all set!"
            )
            input(
                f"\nto use this expense tracker, simply select one of the options in the HOME by entering a number between 1 and {NUM_OF_OPTIONS}. and, if at any point, you want to cancel an operation, just type 'back'. \n\nready to try it out? (enter any key to to continue): "
            )
            print("\nhere is the HOME:")
            self.print_options()
            print(
                "\njust make sure that before you close the app: select '10', to save all your data!"
            )

        # What happens if the user is simply logging in without issues:
        else:
            print(f"hey {self.storage.username}, nice to see you back!")
            self.print_options()

    # Setting-up username and currency:

    def first_time_setup(self):
        raw_username = input(
            "\njust before we start, pelase input your username (you can change it anytime): "
        )
        validated_username = self.validate_string_field(
            raw_username,
            "\nplease input a valid username (you can change it any time): ",
        )

        raw_currency = input(
            f"\nnice to meet you {validated_username}! now please input the symbol of your preferred currency, so I can use it to store your expenses ($, £, €, ecc.): "
        )
        validated_currency = self.validate_string_field(
            raw_currency,
            "\nplease input a valid currency (you can change it any time): ",
        )

        return validated_username, validated_currency

    def print_options(self):
        print("\n-------HOME-------\n")
        print("1 - Add an Expense")
        print("2 - Add a category")
        print("3 - Move expense into category")
        print("4 - Show all expenses")
        print("5 - Calculate total cost of all expenses")
        print("6 - Remove an expense")
        print("7 - Remove a category")
        print("8 - Change username")
        print("9 - Change currency")
        print("10 - Save Data & Exit")

    def get_user_choice(self):
        raw_input = input(f"\n{self.storage.username}, enter 1 - {NUM_OF_OPTIONS}: ")
        return self.validate_user_choice(raw_input)

    def validate_user_choice(self, raw_input):
        while True:
            if not raw_input:
                raw_input = input(
                    "\nyou didn't enter a valid input. please try again: "
                )
                continue

            if not raw_input.isdigit():
                raw_input = input(f"'{raw_input}' is not a number. please try again: ")
                continue

            choice = int(raw_input)
            if choice not in range(1, NUM_OF_OPTIONS + 1):
                raw_input = input(
                    f"'{choice}' is not in range 1 - {NUM_OF_OPTIONS}. please try again: "
                )
                continue

            return choice

    def execute_user_choice(self, user_choice):
        try:
            if user_choice == 1:
                self.add_expense()
            elif user_choice == 2:
                self.add_category()
            elif user_choice == 3:
                self.move_expense_into_category()
            elif user_choice == 4:
                self.show_all_expenses()
            elif user_choice == 5:
                self.calculate_total_cost_of_expenses()
            elif user_choice == 6:
                self.remove_expense()
            elif user_choice == 7:
                self.remove_category()
            elif user_choice == 8:
                self.change_username()
            elif user_choice == 9:
                self.change_currency()
            elif user_choice == 10:
                self.log_out()

        except CancelOperation:
            print("\noperation cancelled")

    # 1. Add Expense:

    def add_expense(self):
        raw_name = input("\ninput the name of the expense you want to add: ")
        validated_name = self.validate_string_field(
            raw_name, "\nyou didn't enter a valid name, please try again: "
        )

        # Checking whether an expense with the same name already exists:
        while True:
            already_exists, categorized, location = self.storage.does_expense_name_already_exist(
                validated_name
            )
            if not already_exists:
                break

            if categorized:
                for expense in location["expenses"]:
                    if expense["name"] == validated_name:
                        expense_cost = expense["cost"]
                        break

                raw_new_expense_name = input(
                    f"\n'{validated_name}' already exists ('{location["name"]}' --> '{validated_name}' - {expense_cost:.2f} {self.storage.currency}) please enter a different name: "
                )
            else:
                raw_new_expense_name = input(
                    f"\n'{validated_name} - {location["cost"]:.2f} {self.storage.currency}' is already an expense, please input a different name: "
                )

            validated_name = self.validate_string_field(raw_new_expense_name, "\nyou didn't enter a valid input, please try again: ")

        raw_cost = input(
            f"\nnow input the cost of '{validated_name}' in {self.storage.currency}: "
        )
        validated_cost = self.validate_cost(raw_cost)

        self.storage.store_expense(validated_name, validated_cost)
        print(
            f"\n'{validated_name}' - {validated_cost:.2f} {self.storage.currency} saved succesfully."
        )

    def validate_string_field(self, field_name, error_message):
        while True:
            if len(field_name.strip()) > 0:
                if field_name == "back":
                    raise CancelOperation
                return field_name
            else:
                field_name = input(error_message)

    def validate_cost(self, cost):
        while True:
            if not cost.strip():
                cost = input("\nyou didn't enter a valid cost. please try again: ")
                continue
            if cost == "back":
                raise CancelOperation

            try:
                amount = float(cost)
            except ValueError:
                cost = input(f"\n'{cost}' is not a number. please try again: ")
                continue

            if amount <= 0:
                cost = input("\nthe cost has to be bigger than 0. please try again: ")
                continue
            return amount

    # 2. Add Category:

    def add_category(self):
        raw_name = input("\ninput the name of the category you want to add: ")
        while True:
            validated_name = self.validate_string_field(
                raw_name, "\nyou didn't enter a valid name, please try again: "
            )  # Checking if the category name that the user input already exist:
            if not self.storage.does_category_name_already_exist(validated_name):
                break
            raw_name = input(
                f"\n'{validated_name}' is already a category, please input a different name: "
            )

        self.storage.store_category(validated_name)

        print(f"\n'{validated_name}' saved succesfully.")

    # 3. Move expense into category:

    def move_expense_into_category(self):
        if not self.ensure_expenses_and_categories_exist():
            return

        expense_prompt = "\nenter the name of the expense you want to move (if you can't remember it: enter 'show' instead, and I will show all your expenses): "

        expense = self.find_item_by_name(
            self.storage.expenses,
            expense_prompt,
            False,
            "\nnow enter the name of the expense you want to move: ",
        )
        if not expense:
            return

        print(f"\n'{expense["name"]}' found in expenses.")

        category_prompt = f"\nenter the name of the category you want '{expense["name"]}' to move into (if you can't remember it: enter 'show' instead, and I will show all your categories): "

        category = self.find_item_by_name(
            self.storage.categories,
            category_prompt,
            expense["name"],
            f"\nnow enter the name of the expense you want '{expense}' to move into: ",
        )

        self.storage.store_expense_into_category(expense, category)
        print(f"\n'{expense["name"]}' succefully moved into {category["name"]}.")
        self.storage.expenses.remove(expense)

    def ensure_expenses_and_categories_exist(self):
        if not self.storage.expenses and not self.storage.categories:
            print(f"\n{self.storage.username}, you don't have any expenses yet!")
            return False

        if not self.storage.expenses:
            print(
                f"\n{self.storage.username}, you don't have any uncategorized expenses yet!"
            )
            return False

        if not self.storage.categories:
            print(f"\n{self.storage.username}, you don't have any categories yet!")
            return False

        return True

    # Helper method for moving expenses into categories which asks for expense name / category name and validates it:
    def find_item_by_name(self, items, item_prompt, expense_name, helper_prompt):
        raw_item_name = input(item_prompt)

        while True:
            validated_item_name = self.validate_string_field(
                raw_item_name, "\nyou didn't enter a valid name, please try again: "
            )
            # If the user can't remember the expenses / categories they have:
            if validated_item_name.lower().strip() == "show":
                validated_item_name = self.reprompt_name_with_help(
                    items, expense_name, helper_prompt
                )

            # Checking whether the expense is already categorized:
            _, categorized, category = self.storage.is_expense_already_categorized(validated_item_name)

            if categorized:
                print(
                    f"\n'{validated_item_name}' is already categorized in '{category["name"]}'."
                )
                return False

            for item in items:
                if item["name"] == validated_item_name:
                    return item

            raw_item_name = input(
                f"\n'{validated_item_name}' does not exist, please try again: "
            )

    def reprompt_name_with_help(self, items, expense_name, helper_prompt):
        self.print_expenses_or_categories_names(items)
        if not expense_name:  # if the user needs to see his expenses:
            raw_item_name = input(helper_prompt)

        else:  # if the user needs to see his categories:
            raw_item_name = input(
                f"\nnow input the name of the category you want '{expense_name}' to move into: "
            )

        validated_item_name = self.validate_string_field(
            raw_item_name, "\nyou didn't enter a valid name, please try again: "
        )
        return validated_item_name

    def print_expenses_or_categories_names(self, items):
        if items is self.storage.expenses:
            print(f"\nhere are your expenses {self.storage.username}:\n")
        else:
            print(f"\nhere are you categories {self.storage.username}:\n")

        for index, item in enumerate(items):
            print(f"{index+1}. {item["name"]}")

    # 4. Show all expenses:

    def show_all_expenses(self):
        if not self.storage.has_expenses():
            print(f"\n{self.storage.username}, you don't have any expenses yet!")
            return

        print(f"\nhere are your expenses {self.storage.username}:\n")
        self.print_expenses_in_categories()
        self.print_expenses_outside_of_categories()

        total_cost = self.storage.calculate_total_cost()
        print("\n____")
        print(f"\nTOTAL COST : {total_cost:,.2f} {self.storage.currency}\n")

    def print_expenses_in_categories(self):
        if self.storage.has_expenses_in_categories():
            print("______Expenses inside categories:______")

            for index, category in enumerate(self.storage.categories):
                prefix = f"{index + 1}. "
                print(f"\n{prefix}{category["name"]}:")

                if not category["expenses"]:
                    print("(no expenses yet!)")
                    continue
                self.print_all_expenses_in_category(category)
                self.print_total_category_cost(category)

    def print_all_expenses_in_category(self, category):
        for expense in category["expenses"]:
            if expense["name"] and expense["cost"]:
                print(
                    f"{expense["name"]} - {expense["cost"]:,.2f} {self.storage.currency}"
                )

    def print_total_category_cost(self, category):
        if len(category["expenses"]) > 1:
            total_category_cost = self.storage.get_category_total_cost(category)
            print(
                f"\n--> total cost of {category["name"]} : {total_category_cost:,.2f} {self.storage.currency}"
            )

    def print_expenses_outside_of_categories(self):
        if self.storage.expenses:
            if self.storage.has_expenses_in_categories():
                print("\n\n______Expenses outside categories:______\n")
            for expense in self.storage.expenses:
                print(
                    f"{expense["name"]} - {expense["cost"]:,.2f} {self.storage.currency}"
                )
            self.print_total_uncategorized_expenses_cost()

    def print_total_uncategorized_expenses_cost(self):
        if len(self.storage.expenses) > 1:
            expenses_outisde_categories_total_cost = 0
            for expense in self.storage.expenses:
                expenses_outisde_categories_total_cost += expense["cost"]

            print(
                f"\n--> total of uncategorized expenses: {expenses_outisde_categories_total_cost:,.2f} {self.storage.currency}"
            )

    # 5. Calculate total cost of expenses:

    def calculate_total_cost_of_expenses(self):
        total_cost = self.storage.calculate_total_cost()
        print(f"\nTotal Cost = {total_cost:,.2f} {self.storage.currency}")

    # 6. Remove an expense:

    def remove_expense(self):
        if not self.storage.has_expenses():
            print(f"\n{self.storage.username}, you have no expenses to remove yet!")
            return

        raw_expense_name = input(
            "input the name of the expense you want to remove (if you can't remember it: enter 'show' instead, and I will show all your expenses): "
        )

        while True:
            validated_expense_name = self.validate_string_field(
                raw_expense_name, "\nyou didn't enter a valid input, please try again: "
            )

            # What happens if the user cannot remember the exact name of the expense they want to remove:
            if validated_expense_name == "show":
                while True:
                    print(f"\nhere are your expenses {self.storage.username}:\n")
                    self._print_expenses_and_categories_without_total_cost()
                    raw_expense_name = input(
                        "\nnow input the name of the expense you want to remove: "
                    )
                    validated_expense_name = self.validate_string_field(
                        raw_expense_name,
                        "\nyou didn't enter a valid input, please try again: ",
                    )
                    if validated_expense_name != "show":
                        break

            # Removing the expense:
            located, expense, location = self.storage.locate_expense(
                validated_expense_name
            )

            if not located:
                raw_expense_name = input(
                    f"\n'{validated_expense_name}' was not found, please try again: "
                )
                continue

            if (
                location == self.storage.expenses
            ):  # if the expense was found in the general expenses list:
                printable_location = "expenses"
            else:  # if the expense was found inside a category:
                printable_location = location["name"]

            # Confirming whether the user wants to delete their expense:
            raw_removal_confirmation = (
                input(
                    f"\n'{validated_expense_name} - {expense["cost"]:.2f}{self.storage.currency}' was found in '{printable_location}'. are you sure you want to remove it? [y/n]: "
                )
                .lower()
                .strip()
            )

            while True:
                validated_removal_confirmation = self.validate_string_field(
                    raw_removal_confirmation,
                    "\nyou didn't enter a valid input, please try again: ",
                )
                if validated_removal_confirmation in ["y", "yes"]:
                    self.storage.remove_expense(expense, location)
                    print(f"\n'{validated_expense_name}' deleted succesfully.")
                    break
                elif validated_removal_confirmation in ["n", "no"]:
                    print("\nDeletion cancelled.")
                    break
                else:
                    raw_removal_confirmation = input(
                        f"\n'{validated_removal_confirmation}' is not a valid input, please try again: "
                    )
            break

    def _print_expenses_and_categories_without_total_cost(self):
        # Printing expenses inside categories:
        if self.storage.has_expenses_in_categories():
            print("______Expenses inside categories:______")

            for index, category in enumerate(self.storage.categories):
                prefix = f"{index + 1}. "
                print(f"\n{prefix}{category["name"]}:")

                if not category["expenses"]:
                    continue

                for expense in category["expenses"]:
                    if expense["name"] and expense["cost"]:
                        print(
                            f"{expense["name"]} - {expense["cost"]:,.2f} {self.storage.currency}"
                        )

        # Print expenses outside of categories:
        if self.storage.expenses:
            if self.storage.has_expenses_in_categories():
                print("\n\n______Expenses outside categories:______\n")
            for expense in self.storage.expenses:
                print(
                    f"{expense["name"]} - {expense["cost"]:,.2f} {self.storage.currency}"
                )

    # 7. Remove category:

    def remove_category(self):
        if not self.storage.has_categories():
            print(f"\n{self.storage.username}, you have no categories to remove yet!")
            return

        raw_category_name = input(
            "\ninput the name of the category you want to remove (if you can't remember it: enter 'show' instead, and I will show all your categories): "
        )

        # Validating the category name that the user wants to delete:
        while True:
            validated_category_name = self.validate_string_field(
                raw_category_name,
                "\nyou didn't enter a valid input, please try again: ",
            )

            # What happens if the user cannot remember the exact name of the category they want to remove:
            if validated_category_name == "show":
                while True:
                    print(f"\nhere are your categories {self.storage.username}:\n")
                    self.print_category_names()

                    raw_category_name = input(
                        "\nnow input the name of the category you want to remove: "
                    )
                    validated_category_name = self.validate_string_field(
                        raw_category_name,
                        "\nyou didn't enter a valid input, please try again: ",
                    )
                    if validated_category_name != "show":
                        break

            exists, category = self.storage.category_already_exists(
                validated_category_name
            )

            if exists:
                print(f"\n'{validated_category_name}' was found in categories.")
                break

            raw_category_name = input(
                f"\n'{validated_category_name}' doesn't exist, please try again: "
            )

        category_has_expenses = self.storage.category_has_expenses(category)

        if category_has_expenses:
            raw_deletion_input = (
                input(
                    f"\n{self.storage.username}, do you want expenses inside '{validated_category_name}' to be deleted as well? (if not, the expenses will simply be moved into your general expenses list and won't be removed) [y/n]: "
                )
                .lower()
                .strip()
            )

            while True:
                validated_deletion_input = self.validate_string_field(
                    raw_deletion_input,
                    "\nyou didn't enter a valid input, please try again: ",
                )

                if validated_deletion_input in ["no", "n"]:
                    self.storage.move_expenses_out_of_category(category)
                    print(
                        f"\nall expenses inside '{validated_category_name}' moved and saved."
                    )
                    break
                elif validated_deletion_input in ["yes", "y"]:
                    print("\nexpenses deleted.")
                    break
                else:
                    raw_deletion_input = input(
                        f"\n'{validated_deletion_input}' is not a valid input, please try again: "
                    )

        self.storage.remove_category(category)
        print(f"\n'{validated_category_name}' deleted succesfully.")

    def print_category_names(self):
        for index, category in enumerate(self.storage.categories):
            prefix = f"{index + 1}. " if len(self.storage.categories) > 1 else ""
            print(f"{prefix}{category["name"]}")

    def change_username(self):
        raw_name = input(f"\n{self.storage.username}, please input your new username: ")
        validated_name = self.validate_string_field(raw_name, "\nyou didn't enter a valid input, please try again: ")

        self.storage.username = validated_name

        print(f"\ninteresting pick {self.storage.username}!")

    def change_currency(self):
        raw_currency = input(
            "\ninput the symbol of your new preferred currency ($, £, €, ecc.): "
        )

        validated_currency = self.validate_string_field(raw_currency, "\nyou didn't enter a valid input, please try again: ")

        self.storage.currency = validated_currency

        print(f"\nCurrency updated to '{self.storage.currency}'.")

    # 10. Log out:

    def log_out(self):
        self.storage.save_data()
        print("\nall data saved succesfully!")
        print(
            f"see you next time {self.storage.username}!"
        )

class CancelOperation(Exception):
    pass

if __name__ == "__main__":
    app = ExpenseTracker()
    app.run()
