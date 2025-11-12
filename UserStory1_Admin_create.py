# ============================================
# User Story #1 – User Admin Create User Account
#
# ============================================

# --- Boundary ---
class CreateAccountPage:
    """
    <<Boundary>> CreateAccountPage
    +submitCreateAcc(username, password): str
    """

    def __init__(self):
        self.controller = AccountController()

    def submitCreateAcc(self, username, password):
        # Pass credentials to controller for processing
        return self.controller.createAccount(username, password)


# --- Controller ---
class AccountController:
    """
    <<Controller>> AccountController
    +createAccount(username, password): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def createAccount(self, username, password):
        # Validate user input before sending to Entity
        if not username or not password:
            return "Invalid or missing fields"
        return self.user_account.createAccount(username, password)


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -userName: str
    -password: str
    +createAccount(username, password): str
    """

    def __init__(self):
        self.accounts = []  # Simulated database

    def createAccount(self, username, password):
        # Add new account to the database
        self.accounts.append({"username": username, "password": password})
        return "Account created successfully"


# --- Run for CLI Testing ---
if __name__ == "__main__":
    page = CreateAccountPage()
    print("\n=== Create New User Account ===")
    u = input("Enter username: ").strip()
    p = input("Enter password: ").strip()
    print(page.submitCreateAcc(u, p))
