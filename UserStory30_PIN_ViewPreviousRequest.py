# ============================================
# User Story #30 - User PIN - View Previous Request
# BCE Structure
# ============================================


# --- Boundary ---
class ViewPrevRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or ViewPrevRequestController()

    def getRequestDetail(self, requestID, requestStatus='Completed'):
        return self.controller.getRequestDetail(requestID, requestStatus)


# --- Controller ---
class ViewPrevRequestController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def getRequestDetail(self, requestID, requestStatus='Completed') -> str:
        if not requestID or not str(requestID).strip():
            return "Error: Request ID is required."

        if not self.load_requests:
            return "Error: load_requests function not provided."

        return self.entity.getRequestDetail(
            requestID,
            requestStatus=requestStatus,
            load_requests_func=self.load_requests
        )


# --- Entity ---
class Request:
    def __init__(self):
        self._PIN = None
        self._requestID = None
        self._requestTitle = None
        self._requestCategory = None
        self._requestStatus = None
        self._requestDescription = None
        self._requestDate = None
        self._requestLocation = None
        self._CSRRepInCharge = None

    def getRequestDetail(self, requestID, requestStatus='Completed', load_requests_func=None) -> str:
        if not load_requests_func:
            return "Error: load_requests function not provided."

        all_requests = load_requests_func()

        for req in all_requests:
            req_id = str(req.get('id', '')).strip()
            if req_id == str(requestID).strip() or req_id.replace('REQ-', '') == str(requestID).strip().replace('REQ-', ''):
                status = str(req.get('status', '')).lower()
                if requestStatus and status != str(requestStatus).lower():
                    return f"Error: Request '{requestID}' is not in requested status '{requestStatus}'."

                self._requestID = req_id
                self._requestTitle = req.get('title', '')
                self._requestCategory = req.get('category', '')
                self._requestStatus = req.get('status', '')
                self._requestDescription = req.get('description', '')
                self._requestDate = req.get('date', '')
                self._requestLocation = req.get('location', '')
                self._PIN = req.get('owner', '')
                self._CSRRepInCharge = req.get('assignee') or req.get('csr') or req.get('CSRRepInCharge') or ''

                return {
                    'id': self._requestID,
                    'title': self._requestTitle,
                    'category': self._requestCategory,
                    'status': self._requestStatus,
                    'description': self._requestDescription,
                    'date': self._requestDate,
                    'location': self._requestLocation,
                    'owner': self._PIN,
                    'csrRepInCharge': self._CSRRepInCharge
                }

        return f"Error: Request with ID '{requestID}' not found."
