# ============================================
# User Story #3 – User Admin Update User Account

# ============================================

# --- Boundary ---
class UpdateAccountPage:
    """
    <<Boundary>> UpdateAccountPage
    +updateAccount(username, password): str
    """

    def __init__(self):
        self.controller = UpdateAccountController()

    def updateAccount(self, username, password):
        # Send data to controller
        return self.controller.submitUpdate(username, password)


# --- Controller ---
class UpdateAccountController:
    """
    <<Controller>> UpdateAccountController
    +submitUpdate(username, password): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def submitUpdate(self, username, password):
        # Check for missing or invalid data
        if not username or not password:
            return "Error: Invalid or missing fields."
        # Call entity layer to update user record
        result = self.user_account.submitUpdate(username, password)
        return result


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -userName: str
    -password: str
    -email: str
    -phone: str
    +submitUpdate(username, password): str
    """

    def __init__(self):
        # Simulated database
        self.accounts = [
            {"userName": "admin01", "password": "admin123", "email": "admin01@sys.com", "phone": "91234567"},
            {"userName": "csr_rep1", "password": "csr123", "email": "csr1@sys.com", "phone": "92345678"},
            {"userName": "pin_user1", "password": "pin321", "email": "pin1@sys.com", "phone": "93456789"},
        ]

    def submitUpdate(self, username, password):
        # Simulate updating password for a user
        for acc in self.accounts:
            if acc["userName"] == username:
                acc["password"] = password
                return "Update successful!"
        return "User not found."


# --- Run for CLI Testing ---
if __name__ == "__main__":
    page = UpdateAccountPage()
    print("\n=== Update User Account ===")
    u = input("Enter username to update: ").strip()
    p = input("Enter new password: ").strip()
    print(page.updateAccount(u, p))
