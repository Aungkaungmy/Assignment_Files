# ============================================
# User Story #5 – User Admin Search User Account
# BCE Structure
# ============================================

# --- Boundary ---
class SearchAccountPage:
    """
    <<Boundary>> SearchAccountPage
    +submitSearch(username, data): str
    """

    def __init__(self):
        self.controller = SearchAccountController()

    def submitSearch(self, username, data):
        # Validate user input before passing to controller
        if not username or not data:
            return "Error: Invalid search input. Please enter both username and data."

        # Send data to controller for processing
        return self.controller.searchAccount(username, data)

    def run(self):
        print("\n=== User Admin – Search User Account ===")
        username = input("Enter your admin username: ").strip()
        data = input("Enter keyword to search user account (e.g., username, email, phone): ").strip()
        result = self.submitSearch(username, data)
        print(result)


# --- Controller ---
class SearchAccountController:
    """
    <<Controller>> SearchAccountController
    +searchAccount(username, data): str
    """

    def __init__(self):
        self.user_account = UserAccount()

    def searchAccount(self, username, data):
        # Controller delegates searching task to Entity
        return self.user_account.searchAccount(username, data)


# --- Entity ---
class UserAccount:
    """
    <<Entity>> UserAccount
    -username: str
    -password: str
    -email: str
    -phone: str
    +searchAccount(username, data): str
    """

    def __init__(self):
        # Simulated user database
        self.accounts = [
            {"username": "john_doe", "password": "abc123", "email": "john@example.com", "phone": "91234567"},
            {"username": "mary_lim", "password": "lim123", "email": "mary@domain.com", "phone": "98765432"},
            {"username": "alex_tan", "password": "tan888", "email": "alex@sample.com", "phone": "90011223"},
        ]

    def searchAccount(self, username, data):
        # Only allow if admin username is valid
        if username.lower() != "admin":
            return "Error: Unauthorized user. Only admins can perform search."

        # Search for user account based on any matching field
        results = []
        for acc in self.accounts:
            if (
                data.lower() in acc["username"].lower()
                or data.lower() in acc["email"].lower()
                or data.lower() in acc["phone"]
            ):
                results.append(acc)

        if not results:
            return f"No results found for '{data}'."

        # Display formatted results
        print("\n--- Search Results ---")
        for r in results:
            print(f"Username: {r['username']}")
            print(f"Password: {r['password']}")
            print(f"Email: {r['email']}")
            print(f"Phone: {r['phone']}")
            print("---------------------")

        return "Search completed successfully."


# --- Run ---
if __name__ == "__main__":
    page = SearchAccountPage()
    page.run()
