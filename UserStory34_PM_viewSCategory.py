# ==============================================================
# User Story #34 – Platform Management: View Service Categories (BCE)
# ==============================================================

# --- Boundary ---
class ViewCategoriesPage:
    def __init__(self):
        self.controller = ViewCategoriesController()

    def viewCategories(self) -> list:
        return self.controller.viewCategories()

    def run(self):
        print("\n=== Platform Management – View Service Categories ===")
        while True:
            print("\n1) View Categories")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                categories = self.viewCategories()
                if not categories:
                    print("No service categories available.")
                else:
                    print("\n--- Available Service Categories ---")
                    for c in categories:
                        print(f"Category ID: {c['categoryID']} | Category Name: {c['categoryName']}")
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("Invalid option. Please try again.")

# --- Controller ---
class ViewCategoriesController:
    def __init__(self):
        self.entity = Category()

    def viewCategories(self) -> list:
        return self.entity.viewCategories()

# --- Entity ---
class Category:
    def __init__(self):
        self.categories = [
            {"categoryID": 1, "categoryName": "Healthcare"},
            {"categoryID": 2, "categoryName": "Transportation"},
            {"categoryID": 3, "categoryName": "Housing"},
            {"categoryID": 4, "categoryName": "Financial Aid"},
            {"categoryID": 5, "categoryName": "Education"},
        ]

    def viewCategories(self) -> list:
        return list(self.categories)

# --- Run ---
if __name__ == "__main__":
    ViewCategoriesPage().run()
