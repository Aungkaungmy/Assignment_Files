# ============================================
# User Story #11 – User Admin Login to User Profile

# ============================================

# --- Boundary ---
class LoginPage:
    """
    <<Boundary>> LoginPage
    +enterCredentials(username, password): str
    """

    def __init__(self):
        self.controller = LoginController()

    def enterCredentials(self, username, password):
        # Forward input to controller
        return self.controller.processLogin(username, password)

    def run(self):
        print("\n=== User Admin Login ===")
        while True:
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            # Call the boundary method
            result = self.enterCredentials(username, password)
            print(result)

            if result == "Login successful!":
                print("\nWelcome to your User Profile Page.")
                print("(You can now manage services and requests.)")
                break

            retry = input("\nTry again? (y/n): ").strip().lower()
            if retry != "y":
                print("Exiting login...")
                break


# --- Controller ---
class LoginController:
    def __init__(self):
        self.user_account = UserAccount()

    def processLogin(self, username, password):
        #  Use the entity’s login() method directly
        result = self.user_account.login(username, password)
        if "successful" in result.lower():
            return "Login successful!"
        else:
            return "Invalid credentials"


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -username: str
    -password: str
    +login(username, password): str
    """

    def __init__(self):
        self.accounts = [
            {"username": "admin1", "password": "pass123"},
            {"username": "admin2", "password": "mypassword"},
            {"username": "admin3", "password": "secure123"},
        ]

    def login(self, username, password):
        # Validate credentials
        for acc in self.accounts:
            if acc["username"] == username and acc["password"] == password:
                return "Login successful!"
        return "Error: Invalid username or password."


# --- Run ---
if __name__ == "__main__":
    page = LoginPage()
    page.run()
