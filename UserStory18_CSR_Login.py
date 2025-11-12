# ============================================
# User Story #18 - User CSR Rep - Log In to Request
# BCE Structure
# ============================================


# --- Boundary ---
class LoginPage:
    def __init__(self, controller=None):
        self.controller = controller or LoginController()

    def enterCredentials(self, username, password, role='csr'):
        return self.controller.processLogin(username, password, role)


# --- Controller ---
class LoginController:
    def __init__(self, entity=None, load_users_func=None, password_checker=None):
        self.entity = entity or UserAccount()
        self.load_users = load_users_func
        self.password_checker = password_checker

    def processLogin(self, username, password, role='csr') -> str:
        if not username or not str(username).strip():
            return "Error: Username is required."
        if password is None or password == '':
            return "Error: Password is required."

        if not self.load_users:
            return "Error: load_users function not provided."

        return self.entity.login(
            username,
            password,
            role=role,
            load_users_func=self.load_users,
            password_checker=self.password_checker
        )


# --- Entity ---
class UserAccount:
    def __init__(self):
        self.username = None
        self.password = None

    def login(self, username, password, role='csr', load_users_func=None, password_checker=None):
        if not load_users_func:
            return "Error: load_users function not provided."

        users = load_users_func()

        target_role = str(role).strip() if role else 'csr'
        if target_role not in users:
            return {
                'success': False,
                'message': f"Role '{target_role}' not found."
            }

        role_accounts = users.get(target_role, {})
        account = role_accounts.get(username)
        if not account:
            return {
                'success': False,
                'message': 'Account not found.'
            }

        stored_password = account.get('password')
        is_valid = False
        if password_checker and stored_password:
            try:
                is_valid = password_checker(stored_password, password)
            except TypeError:
                is_valid = password_checker(password, stored_password)
        else:
            is_valid = stored_password == password

        if not is_valid:
            return {
                'success': False,
                'message': 'Invalid credentials.'
            }

        self.username = username
        self.password = stored_password

        return {
            'success': True,
            'message': 'Login successful!',
            'role': target_role,
            'account': {
                'username': username,
                'role': target_role
            }
        }
