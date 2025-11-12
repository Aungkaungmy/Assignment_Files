# ==========================================================
# User Story #9 – User Admin: Suspend User Profile
# ==========================================================

class SuspendProfilePage:
    def __init__(self):
        self.controller = SuspendProfileController()

    def suspendConfirm(self):
        confirm = input("Confirm suspension? (yes/no): ").lower()
        return confirm == "yes"

    def suspendProfile(self):
        user_id = int(input("Enter User Profile ID to suspend: "))
        user_name = input("Enter User Profile Name: ")
        if not self.suspendConfirm():
            return "Suspension cancelled."
        result = self.controller.suspendProfile(user_id, user_name)
        return result

    def run(self):
        print("\n=== User Admin - Suspend User Profile ===")
        while True:
            print("\n1. Suspend User Profile")
            print("2. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                try:
                    result = self.suspendProfile()
                    print(f"\n{result}")
                except ValueError:
                    print("Invalid ID.")
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")


class SuspendProfileController:
    def __init__(self):
        self.userProfile = UserProfile()

    def suspendProfile(self, userProfileID, userProfileName):
        user = self.userProfile.findProfile(userProfileID)
        if not user:
            return "User profile not found."
        if user["userProfileName"].lower() != userProfileName.lower():
            return "User name does not match ID."
        return self.userProfile.suspendProfile(userProfileID)


class UserProfile:
    def __init__(self):
        self.userProfiles = [
            {"userProfileID": 1, "userProfileName": "Alice", "userRole": "CSR", "status": "Active"},
            {"userProfileID": 2, "userProfileName": "Bob", "userRole": "PIN", "status": "Active"},
            {"userProfileID": 3, "userProfileName": "Clara", "userRole": "Admin", "status": "Active"},
        ]

    def findProfile(self, userProfileID):
        for profile in self.userProfiles:
            if profile["userProfileID"] == userProfileID:
                return profile
        return None

    def suspendProfile(self, userProfileID):
        for profile in self.userProfiles:
            if profile["userProfileID"] == userProfileID:
                if profile["status"] == "Suspended":
                    return "Profile is already suspended."
                profile["status"] = "Suspended"
                return f"Profile {profile['userProfileName']} suspended successfully."
        return "User profile not found."


if __name__ == "__main__":
    page = SuspendProfilePage()
    page.run()
