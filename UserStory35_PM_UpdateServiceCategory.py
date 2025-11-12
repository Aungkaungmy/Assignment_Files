# ==============================================================
# User Story #35 – Platform Management: Update Service Category (BCE)
# ==============================================================

# --- Boundary ---
class UpdateCategoryPage:
    def __init__(self):
        self.controller = UpdateCategoryController()

    def updateInfo(self, categoryID: int, newName: str) -> str:
        name = newName.strip()
        if not isinstance(categoryID, int) or categoryID <= 0 or not name:
            return "error message"
        return self.controller.submitUpdate(categoryID, name)

    def run(self):
        print("\n=== Platform Management – Update Service Category ===")
        while True:
            print("\n1) Update Category")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                try:
                    cid = int(input("Enter Category ID to update: ").strip())
                except ValueError:
                    print("error message")
                    continue
                new_name = input("Enter new Category Name: ")
                print(self.updateInfo(cid, new_name))
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("error message")

# --- Controller ---
class UpdateCategoryController:
    def __init__(self):
        self.entity = Category()

    def submitUpdate(self, categoryID: int, newName: str) -> str:
        return self.entity.submitUpdate(categoryID, newName)

# --- Entity ---
class Category:
    def __init__(self):
        self.categories = [
            {"categoryID": 1, "categoryName": "Healthcare"},
            {"categoryID": 2, "categoryName": "Transportation"},
            {"categoryID": 3, "categoryName": "Housing"},
            {"categoryID": 4, "categoryName": "Financial Aid"},
        ]

    def submitUpdate(self, categoryID: int, newName: str) -> str:
        for c in self.categories:
            if c["categoryID"] == categoryID:
                if not newName.strip():
                    return "error message"
                c["categoryName"] = newName
                return "successful"
        return "error message"

# --- Run ---
if __name__ == "__main__":
    UpdateCategoryPage().run()
