# ============================================
# User Story #19 - User PIN - Log Out of Request
# BCE Structure
# ============================================


# --- Boundary ---
class LogoutPage:
    def __init__(self, controller=None):
        self.controller = controller or LogoutPageController()

    def submitLogout(self, username=None, role='pin'):
        return self.controller.processLogout(username=username, role=role)


# --- Controller ---
class LogoutPageController:
    def __init__(self, entity=None, session_manager=None):
        self.entity = entity or UserAccount()
        self.session_manager = session_manager

    def processLogout(self, username=None, role='pin') -> str:
        return self.entity.logout(username=username, role=role, session_manager=self.session_manager)


# --- Entity ---
class UserAccount:
    def __init__(self):
        self.username = None
        self.role = None

    def logout(self, username=None, role='pin', session_manager=None):
        if session_manager:
            try:
                session_manager()
            except TypeError:
                session_manager.clear()

        self.username = username
        self.role = role

        return {
            'success': True,
            'message': 'Successfully logged out.',
            'role': role,
            'username': username
        }
