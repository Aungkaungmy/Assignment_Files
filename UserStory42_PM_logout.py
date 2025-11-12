# ============================================
# User Story #42 – Platform Management Logout
# BCE Structure
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
        # Boundary action that triggers logout through controller
        confirm = input("Do you want to log out? (y/n): ").strip().lower()
        if confirm == "y":
            return self.controller.submitLogout()
        else:
            return "Logout cancelled."

    def run(self):
        print("\n=== Platform Management Logout ===")
        msg = self.submitLogout()
        print(msg)


# --- Controller ---
class LogOutPageController:
    """
    <<Controller>> LogOutPageController
    +submitLogout(): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def submitLogout(self):
        # Delegate logout action to Entity
        return self.user_account.submitLogout()


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    +submitLogout(): str
    """

    def __init__(self):
        self.is_logged_in = True

    def submitLogout(self):
        # Return fixed success message (UML expected “successful”)
        if self.is_logged_in:
            self.is_logged_in = False
            return "Logout successful."
        return "No active session found."


# --- Run ---
if __name__ == "__main__":
    page = LogoutPage()
    page.run()
