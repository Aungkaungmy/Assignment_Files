# ================================================
# User Story #33 – Platform Management: Create Service Category (BCE)
# ================================================

# --- Boundary ---
class CreateCategoryPage:
    def __init__(self):
        self.controller = CreateCategoryController()

    def submitCreateCategory(self, categoryName: str) -> str:
        name = categoryName.strip()
        if not name:
            return "Error: Category name cannot be empty."
        return self.controller.createCategory(name)

    def run(self):
        print("\n=== Platform Management - Create Service Category ===")
        while True:
            print("\n1. Create Category")
            print("2. Exit")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                categoryName = input("Enter new category name: ")
                print(self.submitCreateCategory(categoryName))
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Try again.")

# --- Controller ---
class CreateCategoryController:
    def __init__(self):
        self.entity = Category()

    def createCategory(self, categoryName: str) -> str:
        return self.entity.createCategory(categoryName)

# --- Entity ---
class Category:
    def __init__(self):
        self.categories = [
            {"categoryID": 1, "categoryName": "Healthcare"},
            {"categoryID": 2, "categoryName": "Transportation"},
            {"categoryID": 3, "categoryName": "Housing"},
        ]

    def createCategory(self, categoryName: str) -> str:
        for c in self.categories:
            if c["categoryName"].lower() == categoryName.lower():
                return "error message"
        newID = len(self.categories) + 1
        self.categories.append({"categoryID": newID, "categoryName": categoryName})
        return "successful"

# --- Run ---
if __name__ == "__main__":
    CreateCategoryPage().run()
