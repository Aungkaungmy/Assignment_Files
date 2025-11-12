# ================================================
# User Story #38 – Platform Management: Generate Daily Report (BCE)
# ================================================

# --- Boundary ---
class GenerateReportPage:
    def __init__(self):
        self.controller = GenerateReportController()

    def submitGenerateReport(self, dateOption: str = "daily") -> str:
        if dateOption.strip().lower() != "daily":
            return "error message"
        return self.controller.generateReport(dateOption)

    def run(self):
        print("\n=== Platform Management - Generate Daily Report ===")
        while True:
            print("\n1) Generate Daily Report")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                print(self.submitGenerateReport("daily"))
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("error message")

# --- Controller ---
class GenerateReportController:
    def __init__(self):
        self.category = Category()
        self.userProfile = UserProfile()
        self.request = Request()

    def generateReport(self, dateOption: str) -> str:
        cats = self.category.generateReport()
        users = self.userProfile.generateReport()
        reqs = self.request.generateReport(dateOption)
        pending = len(reqs["Pending"])
        assigned = len(reqs["Assigned"])
        completed = len(reqs["Completed"])
        return (
            "Report (daily)\n"
            f"Categories: {len(cats)}\n"
            f"UserProfiles: {len(users)}\n"
            f"Requests Pending: {pending}\n"
            f"Requests Assigned: {assigned}\n"
            f"Requests Completed: {completed}"
        )

# --- Entity: Category ---
class Category:
    def __init__(self):
        self.categories = [
            {"categoryID": 1, "categoryName": "Healthcare"},
            {"categoryID": 2, "categoryName": "Education"},
            {"categoryID": 3, "categoryName": "Transport"},
        ]

    def generateReport(self) -> list:
        return list(self.categories)

# --- Entity: UserProfile ---
class UserProfile:
    def __init__(self):
        self.users = [
            {"userProfileID": 1, "userProfileName": "Alice", "userRole": "CSR", "userProfileStatus": "Active"},
            {"userProfileID": 2, "userProfileName": "Bob", "userRole": "PIN", "userProfileStatus": "Active"},
            {"userProfileID": 3, "userProfileName": "Charlie", "userRole": "CSR", "userProfileStatus": "Inactive"},
        ]

    def generateReport(self) -> list:
        return list(self.users)

# --- Entity: Request ---
class Request:
    def __init__(self):
        self.requests = [
            {"requestID": 1, "requestTitle": "Medical Aid", "requestCategory": "Healthcare", "requestStatus": "Pending", "requestDate": "2025-11-09"},
            {"requestID": 2, "requestTitle": "Transport Help", "requestCategory": "Transport", "requestStatus": "Assigned", "requestDate": "2025-11-09"},
            {"requestID": 3, "requestTitle": "Education Support", "requestCategory": "Education", "requestStatus": "Completed", "requestDate": "2025-11-09"},
            {"requestID": 4, "requestTitle": "Wheelchair", "requestCategory": "Healthcare", "requestStatus": "Pending", "requestDate": "2025-11-09"},
        ]

    def generateReport(self, dateOption: str) -> dict:
        out = {"Pending": [], "Assigned": [], "Completed": []}
        for r in self.requests:
            if r["requestStatus"] in out:
                out[r["requestStatus"]].append({"requestDate": r["requestDate"], "requestStatus": r["requestStatus"]})
        return out

# --- Run ---
if __name__ == "__main__":
    GenerateReportPage().run()
