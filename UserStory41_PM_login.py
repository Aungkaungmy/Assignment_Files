# ============================================
# User Story #41 – Platform Management Log In to System
# BCE Structure
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
        # Pass input to controller and return response
        return self.controller.processLogin(username, password)

    def run(self):
        print("\n=== Platform Management Login ===")

        while True:
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            result = self.enterCredentials(username, password)
            print(result)

            if result == "Login successful!":
                print("Access granted to dashboard.")
                break

            retry = input("Try again? (y/n): ").strip().lower()
            if retry != "y":
                print("Exiting login page...")
                break


# --- Controller ---
class LoginController:
    def __init__(self):
        self.user_account = UserAccount()

    def login(self, username, password):
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
            {"username": "pm_admin", "password": "admin123"},
            {"username": "manager1", "password": "secure001"},
            {"username": "supervisor", "password": "pass789"},
        ]

    def login(self, username, password):
        for acc in self.accounts:
            if acc["username"] == username and acc["password"] == password:
                return "Login successful!"
        return "Error: Invalid username or password."


# --- Run ---
if __name__ == "__main__":
    page = LoginPage()
    page.run()
