# ============================================
# User Story #6 – User Admin Create Profile
# BCE Structure
# ============================================

# --- Boundary ---
class CreateProfilePage:
    """
    <<Boundary>> CreateProfilePage
    +submitCreateProfile(fullName, email, username, password, userRole, status): str
    """

    def __init__(self):
        self.controller = CreateProfileController()

    def submitCreateProfile(self, fullName, email, username, password, userRole, status):
        if not fullName or not email or not username or not password or not userRole or not status:
            return "Error: Invalid input. All fields are required."
        return self.controller.createProfile(fullName, email, username, password, userRole, status)

    def run(self):
        print("\n=== User Admin – Create User Account ===")
        fullName = input("Enter Full Name: ").strip()
        email = input("Enter Email: ").strip()
        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()
        userRole = input("Enter User Role (e.g., Admin / CSR / Manager): ").strip()
        status = "Active"
        result = self.submitCreateProfile(fullName, email, username, password, userRole, status)
        print(result)


# --- Controller ---
class CreateProfileController:
    """
    <<Controller>> CreateProfileController
    +createProfile(fullName, email, username, password, userRole, status): str
    """

    def __init__(self):
        self.entity = UserAccount()

    def createProfile(self, fullName, email, username, password, userRole, status):
        return self.entity.createProfile(fullName, email, username, password, userRole, status)


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -fullName: str
    -email: str
    -username: str
    -password: str
    -userRole: str
    -status: str
    +createProfile(fullName, email, username, password, userRole, status): str
    """

    def __init__(self):
        self.accounts = []

    def createProfile(self, fullName, email, username, password, userRole, status):
        for acc in self.accounts:
            if acc["username"] == username or acc["email"] == email:
                return f"Error: Account with username '{username}' or email '{email}' already exists."
        new_account = {
            "fullName": fullName,
            "email": email,
            "username": username,
            "password": password,
            "userRole": userRole,
            "status": status
        }
        self.accounts.append(new_account)
        return f"Account '{fullName}' created successfully with status {status}."


# --- Run ---
if __name__ == "__main__":
    page = CreateProfilePage()
    page.run()
