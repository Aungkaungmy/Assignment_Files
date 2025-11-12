# ============================================
# User Story #12 – User Admin Logout User Profile

# ============================================

# --- Boundary ---
class LogoutPage:
    """
    <<Boundary>> LogoutPage
    +submitLogout(): str
    """

    def __init__(self):
        self.controller = LogOutPageController()

    def submitLogout(self):
        # Send logout request to controller
        return self.controller.submitLogout()

    def run(self):
        print("\n=== Logout Page ===")
        choice = input("Do you want to log out? (y/n): ").strip().lower()
        if choice == "y":
            result = self.submitLogout()
            print(result)
        else:
            print("Logout cancelled.")


# --- Controller ---
class LogOutPageController:
    """
    <<Controller>> LogOutPageController
    +submitLogout(): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def submitLogout(self):
        # Delegate to Entity
        return self.user_account.submitLogout()


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    +submitLogout(): str
    """

    def __init__(self):
        self.is_logged_in = True  # Example session flag

    def submitLogout(self):
        if self.is_logged_in:
            self.is_logged_in = False
            return "Logout successful."
        else:
            return "No active session found."


# --- Run ---
if __name__ == "__main__":
    page = LogoutPage()
    page.run()
