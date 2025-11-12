# ============================================
# User Story #2 – User Admin View User Account

# ============================================

# --- Boundary ---
class ViewAccountPage:
    """
    <<Boundary>> ViewAccountPage
    +getUserDetails(username, password): str
    """

    def __init__(self):
        self.controller = ViewAccountController()

    def getUserDetails(self, username, password):
        # Call controller to handle retrieval
        return self.controller.getUserDetails(username, password)


# --- Controller ---
class ViewAccountController:
    """
    <<Controller>> ViewAccountController
    +getUserDetails(username, password): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def getUserDetails(self, username, password):
        # Retrieve user info from entity
        details = self.user_account.getUserDetails(username, password)
        if details:
            return (
                f"Username: {details['userName']}, "
                f"Password: {details['password']}, "
                f"Email: {details['email']}, "
                f"Phone: {details['phone']}"
            )
        return "Invalid username or password."


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -userName: str
    -password: str
    -email: str
    -phone: str
    +getUserDetails(username, password): str
    """

    def __init__(self):
        # Simulated database
        self.accounts = [
            {"userName": "admin01", "password": "admin123", "email": "admin01@sys.com", "phone": "91234567"},
            {"userName": "csr_rep1", "password": "csr123", "email": "csr1@sys.com", "phone": "92345678"},
            {"userName": "pin_user1", "password": "pin321", "email": "pin1@sys.com", "phone": "93456789"},
        ]

    def getUserDetails(self, username, password):
        # Match credentials and return details
        for acc in self.accounts:
            if acc["userName"] == username and acc["password"] == password:
                return acc
        return None


# --- Run for CLI Testing ---
if __name__ == "__main__":
    page = ViewAccountPage()
    print("\n=== View User Account ===")
    u = input("Enter username: ").strip()
    p = input("Enter password: ").strip()
    print(page.getUserDetails(u, p))
