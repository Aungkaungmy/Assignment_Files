# ============================================
# User Story #7 – User Admin View User Profile
# BCE Structure
# ============================================

# --- Boundary ---
class ViewProfilePage:
    """
    <<Boundary>> ViewProfilePage
    +getProfileDetails(userProfileID): str
    """

    def __init__(self):
        self.controller = ViewProfileController()

    def getProfileDetails(self, userProfileID):
        if not userProfileID:
            return "Error: Please enter a valid User Profile ID."
        return self.controller.getProfileDetails(userProfileID)

    def run(self):
        print("\n=== User Admin – View User Profile ===")
        try:
            userProfileID = int(input("Enter User Profile ID to view: ").strip())
        except ValueError:
            print("Error: Profile ID must be an integer.")
            return
        result = self.getProfileDetails(userProfileID)
        print(result)


# --- Controller ---
class ViewProfileController:
    """
    <<Controller>> ViewProfileController
    +getProfileDetails(userProfileID): str
    """

    def __init__(self):
        self.entity = UserProfile()

    def getProfileDetails(self, userProfileID):
        return self.entity.getProfileDetails(userProfileID)


# --- Entity ---
class UserProfile:
    """
    <<Entity>> UserProfile
    -userProfileID: int
    -userProfileName: str
    -userRole: str
    -status: str
    +getProfileDetails(userProfileID): str
    """

    def __init__(self):
        self.profiles = [
            {"userProfileID": 101, "userProfileName": "John Doe", "userRole": "Admin", "status": "Active"},
            {"userProfileID": 102, "userProfileName": "Mary Tan", "userRole": "Manager", "status": "Active"},
            {"userProfileID": 103, "userProfileName": "Alex Lim", "userRole": "CSR", "status": "Inactive"},
        ]

    def getProfileDetails(self, userProfileID):
        for p in self.profiles:
            if p["userProfileID"] == userProfileID:
                profile_info = (
                    f"\n--- User Profile Found ---\n"
                    f"User Profile ID: {p['userProfileID']}\n"
                    f"User Profile Name: {p['userProfileName']}\n"
                    f"User Role: {p['userRole']}\n"
                    f"Status: {p['status']}\n"
                )
                return profile_info
        return "No user profile found."


# --- Run ---
if __name__ == "__main__":
    page = ViewProfilePage()
    page.run()
