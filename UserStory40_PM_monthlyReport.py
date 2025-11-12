# ================================================
# User Story #40 – Platform Management: Generate Monthly Report (BCE)
# ================================================

# --- Boundary ---
class GenerateReportPage:
    def __init__(self):
        self.controller = GenerateReportController()

    def submitGenerateReport(self, dateOption: str = "monthly") -> str:
        if dateOption.strip().lower() != "monthly":
            return "error message"
        return self.controller.generateReport(dateOption)

    def run(self):
        print("\n=== Platform Management - Generate Monthly Report ===")
        while True:
            print("\n1) Generate Monthly Report")
            print("2) Exit")
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                print(self.submitGenerateReport("monthly"))
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
        reqs = self.request.generateReport(dateOption)  # dict of lists
        pending = len(reqs["Pending"])
        assigned = len(reqs["Assigned"])
        completed = len(reqs["Completed"])
        return (
            "Report (monthly)\n"
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
            {"categoryID": 4, "categoryName": "Food Assistance"},
        ]

    def generateReport(self) -> list:
        return list(self.categories)

# --- Entity: UserProfile ---
class UserProfile:
    def __init__(self):
        self.users = [
            {"userProfileID": 1, "userProfileName": "Alice", "userRole": "CSR", "userProfileStatus": "Active"},
            {"userProfileID": 2, "userProfileName": "Bob", "userRole": "PIN", "userProfileStatus": "Active"},
            {"userProfileID": 3, "userProfileName": "Clara", "userRole": "CSR", "userProfileStatus": "Inactive"},
            {"userProfileID": 4, "userProfileName": "Daniel", "userRole": "Admin", "userProfileStatus": "Active"},
            {"userProfileID": 5, "userProfileName": "Emma", "userRole": "CSR", "userProfileStatus": "Active"},
        ]

    def generateReport(self) -> list:
        return list(self.users)

# --- Entity: Request ---
class Request:
    def __init__(self):
        self.requests = [
            {"PIN": "P001", "requestID": 1, "requestTitle": "Healthcare Outreach",
             "requestCategory": "Healthcare", "requestStatus": "Pending",
             "requestDescription": "Vaccination drive", "requestDate": "2025-11-01",
             "requestLocation": "Bukit Timah", "CSRRepInCharge": "CSR_Alice", "shortlisted": True},
            {"PIN": "P002", "requestID": 2, "requestTitle": "Food Drive Expansion",
             "requestCategory": "Food Assistance", "requestStatus": "Assigned",
             "requestDescription": "Monthly food distribution", "requestDate": "2025-11-10",
             "requestLocation": "Jurong West", "CSRRepInCharge": "CSR_Bob", "shortlisted": True},
            {"PIN": "P003", "requestID": 3, "requestTitle": "Transport Aid Program",
             "requestCategory": "Transport", "requestStatus": "Completed",
             "requestDescription": "Elderly transport", "requestDate": "2025-11-18",
             "requestLocation": "Tampines", "CSRRepInCharge": "CSR_Clara", "shortlisted": False},
            {"PIN": "P004", "requestID": 4, "requestTitle": "School Tutoring Drive",
             "requestCategory": "Education", "requestStatus": "Completed",
             "requestDescription": "Monthly tutoring", "requestDate": "2025-11-25",
             "requestLocation": "Woodlands", "CSRRepInCharge": "CSR_Daniel", "shortlisted": True},
        ]

    def generateReport(self, dateOption: str = "monthly") -> dict:
        out = {"Pending": [], "Assigned": [], "Completed": []}
        for r in self.requests:
            if r["requestStatus"] in out:
                out[r["requestStatus"]].append(
                    {"requestDate": r["requestDate"], "requestStatus": r["requestStatus"]}
                )
        return out

# --- Run ---
if __name__ == "__main__":
    GenerateReportPage().run()
