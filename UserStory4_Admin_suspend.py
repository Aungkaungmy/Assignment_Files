# ============================================
# User Story #4 – User Admin Suspend User Account
# BCE Structure
# ============================================

# --- Boundary ---
class SuspendAccountPage:
    """
    <<Boundary>> SuspendAccountPage
    +suspendConfirm(): str
    +suspendAccount(): str
    """

    def __init__(self):
        self.controller = SuspendAccountController()

    def suspendConfirm(self):
        confirm = input("Do you want to suspend a user account? (y/n): ").strip().lower()
        if confirm == "y":
            return self.suspendAccount()
        else:
            return "Suspension cancelled."

    def suspendAccount(self):
        username = input("Enter username to suspend: ").strip()
        password = input("Enter admin password: ").strip()
        result = self.controller.suspendAccount(username, password)
        return result

    def run(self):
        print("\n=== User Admin – Suspend User Account ===")
        msg = self.suspendConfirm()
        print(msg)


# --- Controller ---
class SuspendAccountController:
    """
    <<Controller>> SuspendAccountController
    +suspendAccount(username, password): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def suspendAccount(self, username, password):
        # Delegate validation and update to Entity
        return self.user_account.suspendAccount(username, password)


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -username: str
    -password: str
    +suspendAccount(username, password): str
    """

    def __init__(self):
        # Simulated user database
        self.accounts = [
            {"username": "john_doe", "password": "pass123", "status": "Active"},
            {"username": "mary_lim", "password": "qwerty", "status": "Active"},
            {"username": "admin_user", "password": "admin123", "status": "Active"},
        ]

    def suspendAccount(self, username, password):
        # Find the account in the database
        for acc in self.accounts:
            if acc["username"] == username:
                # Only allow suspension if admin password is valid
                if password == "admin123":
                    if acc["status"] == "Suspended":
                        return "Account already suspended."
                    acc["status"] = "Suspended"
                    return "Suspension successful."
                else:
                    return "Error: Invalid admin password."
        return "Error: User account not found."


# --- Run ---
if __name__ == "__main__":
    page = SuspendAccountPage()
    page.run()
