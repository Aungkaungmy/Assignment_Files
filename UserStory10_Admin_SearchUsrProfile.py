# ==========================================================
# User Story #10 – User Admin: Search User Profile
# ==========================================================

class SearchProfilePage:
    def __init__(self):
        self.controller = SearchProfileController()

    def submitSearch(self, userProfileID, userProfileName):
        return self.controller.searchProfile(userProfileID, userProfileName)

    def run(self):
        print("\n=== User Admin - Search User Profile ===")
        while True:
            print("\n1. Search User Profile")
            print("2. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                try:
                    user_id = int(input("Enter User Profile ID: "))
                    name = input("Enter User Profile Name: ")
                    result = self.submitSearch(user_id, name)
                    print(f"\n{result}")
                except ValueError:
                    print("Invalid ID.")
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")


class SearchProfileController:
    def __init__(self):
        self.userProfile = UserProfile()

    def searchProfile(self, userProfileID, userProfileName):
        result = self.userProfile.searchProfile(userProfileID, userProfileName)
        if result:
            return f"User Found → ID: {result['userProfileID']}, Name: {result['userProfileName']}, Role: {result['userRole']}, Status: {result['status']}"
        return "Error: No matching user found."


class UserProfile:
    def __init__(self):
        self.userProfiles = [
            {"userProfileID": 1, "userProfileName": "Alice", "userRole": "CSR", "status": "Active"},
            {"userProfileID": 2, "userProfileName": "Bob", "userRole": "PIN", "status": "Suspended"},
            {"userProfileID": 3, "userProfileName": "Clara", "userRole": "Admin", "status": "Active"},
        ]

    def searchProfile(self, userProfileID, userProfileName):
        for profile in self.userProfiles:
            if profile["userProfileID"] == userProfileID or profile["userProfileName"].lower() == userProfileName.lower():
                return profile
        return None


if __name__ == "__main__":
    page = SearchProfilePage()
    page.run()
