# ================================================
# User Story #36 – Platform Management: Delete Service Category (BCE)
# ================================================

# --- Boundary ---
class DeleteCategoryPage:
    def __init__(self):
        self.controller = DeleteCategoryController()

    def deleteCategory(self, categoryID: int) -> str:
        return "confirmation"

    def deleteConfirm(self, categoryID: int) -> str:
        return self.controller.deleteRequest(categoryID)

    def run(self):
        print("\n=== Platform Management – Delete Service Category ===")
        while True:
            print("\n1) Delete Category")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                try:
                    cid = int(input("Enter Category ID: ").strip())
                except ValueError:
                    print("unsuccessful")
                    continue
                print(self.deleteCategory(cid))
                confirm = input("Confirm deletion? (yes/no): ").strip().lower()
                if confirm == "yes":
                    print(self.deleteConfirm(cid))
                else:
                    print("unsuccessful")
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("unsuccessful")

# --- Controller ---
class DeleteCategoryController:
    def __init__(self):
        self.entity = Category()

    def deleteRequest(self, categoryID: int) -> str:
        return self.entity.deleteRequest(categoryID)

# --- Entity ---
class Category:
    def __init__(self):
        self.categories = [
            {"categoryID": 1, "categoryName": "Healthcare"},
            {"categoryID": 2, "categoryName": "Transportation"},
            {"categoryID": 3, "categoryName": "Housing"},
            {"categoryID": 4, "categoryName": "Financial Aid"},
        ]

    def deleteRequest(self, categoryID: int) -> str:
        for c in list(self.categories):
            if c["categoryID"] == categoryID:
                self.categories.remove(c)
                return "successful"
        return "unsuccessful"

# --- Run ---
if __name__ == "__main__":
    DeleteCategoryPage().run()
