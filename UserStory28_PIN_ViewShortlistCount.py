# ============================================
# User Story #28 - User PIN - View Request Shortlist Count
# BCE Structure
# ============================================


# --- Boundary ---
class ShortlistCountPage:
    def __init__(self, controller=None):
        self.controller = controller or ShortlistCountController()

    def showShortlistCount(self, requestID):
        return self.controller.showShortlistCount(requestID)


# --- Controller ---
class ShortlistCountController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def showShortlistCount(self, requestID) -> int:
        if not requestID or not str(requestID).strip():
            return "Error: Request ID is required."

        if not self.load_requests:
            return "Error: load_requests function not provided."

        return self.entity.showShortlistCount(
            requestID,
            load_requests_func=self.load_requests
        )


# --- Entity ---
class Request:
    def __init__(self):
        self._shortlistCount = 0

    def showShortlistCount(self, requestID, load_requests_func=None) -> int:
        if not load_requests_func:
            return "Error: load_requests function not provided."

        all_requests = load_requests_func()

        for req in all_requests:
            req_id = str(req.get('id', '')).strip()
            if req_id == str(requestID).strip() or req_id.replace('REQ-', '') == str(requestID).strip().replace('REQ-', ''):
                raw_value = req.get('shortlistCount')
                if raw_value is None:
                    raw_value = req.get('shortlist_count')
                if raw_value is None:
                    shortlist_by = req.get('shortlisted_by') or req.get('shortlist') or req.get('favorites')
                    if isinstance(shortlist_by, list):
                        raw_value = len(shortlist_by)
                    elif isinstance(shortlist_by, str) and shortlist_by.strip():
                        raw_value = len([v for v in shortlist_by.split(',') if v.strip()])
                    else:
                        raw_value = 0

                try:
                    self._shortlistCount = int(raw_value)
                except (TypeError, ValueError):
                    self._shortlistCount = 0

                return self._shortlistCount

        return f"Error: Request with ID '{requestID}' not found."
