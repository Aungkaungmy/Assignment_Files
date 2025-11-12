# ================================================
# User Story #37 – Platform Management: Search Service Category (BCE)
# ================================================

# --- Boundary ---
class SearchCategoryPage:
    def __init__(self):
        self.controller = SearchCategoryController()

    def submitSearch(self, data: str) -> str:
        q = data.strip()
        if not q:
            return "error message"
        return self.controller.searchCategory(q)

    def run(self):
        print("\n=== Platform Management - Search Service Category ===")
        while True:
            print("\n1) Search Category")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                keyword = input("Enter keyword: ")
                print(self.submitSearch(keyword))
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("error message")

# --- Controller ---
class SearchCategoryController:
    def __init__(self):
        self.entity = Category()

    def searchCategory(self, data: str) -> str:
        return self.entity.searchCategory(data)

# --- Entity ---
class Category:
    def __init__(self):
        self.categories = [
            {"categoryID": 1, "categoryName": "Healthcare"},
            {"categoryID": 2, "categoryName": "Transportation"},
            {"categoryID": 3, "categoryName": "Housing"},
            {"categoryID": 4, "categoryName": "Financial Aid"},
        ]

    def searchCategory(self, data: str) -> str:
        hits = [f"{c['categoryID']}, {c['categoryName']}"
                for c in self.categories
                if data.lower() in c["categoryName"].lower()]
        return "\n".join(hits) if hits else "error message"

# --- Run ---
if __name__ == "__main__":
    SearchCategoryPage().run()
