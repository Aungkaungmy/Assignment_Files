# ==========================================================
# User Story #8 – User Admin: Update User Profile
# ==========================================================

class UpdateProfilePage:
    def __init__(self):
        self.controller = UpdateProfileController()

    def updateProfile(self, userProfileID, userProfileName):
        return self.controller.submitUpdate(userProfileID, userProfileName)

    def run(self):
        print("\n=== User Admin - Update User Profile ===")
        while True:
            print("\n1. Update User Profile")
            print("2. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                try:
                    user_id = int(input("Enter User Profile ID: "))
                    new_name = input("Enter New User Name: ")
                    result = self.updateProfile(user_id, new_name)
                    print(f"\n{result}")
                except ValueError:
                    print("Invalid ID.")
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")


class UpdateProfileController:
    def __init__(self):
        self.userProfile = UserProfile()

    def submitUpdate(self, userProfileID, userProfileName):
        user = self.userProfile.findProfile(userProfileID)
        if not user:
            return "User profile not found."
        return self.userProfile.updateProfile(userProfileID, userProfileName)


class UserProfile:
    def __init__(self):
        self.userProfiles = [
            {"userProfileID": 1, "userProfileName": "Alice", "userRole": "CSR"},
            {"userProfileID": 2, "userProfileName": "Bob", "userRole": "PIN"},
            {"userProfileID": 3, "userProfileName": "Clara", "userRole": "Admin"},
        ]

    def findProfile(self, userProfileID):
        for profile in self.userProfiles:
            if profile["userProfileID"] == userProfileID:
                return profile
        return None

    def updateProfile(self, userProfileID, userProfileName):
        for profile in self.userProfiles:
            if profile["userProfileID"] == userProfileID:
                old_name = profile["userProfileName"]
                profile["userProfileName"] = userProfileName
                return f"Profile updated successfully! ({old_name} → {userProfileName})"
        return "User profile not found."


if __name__ == "__main__":
    page = UpdateProfilePage()
    page.run()
