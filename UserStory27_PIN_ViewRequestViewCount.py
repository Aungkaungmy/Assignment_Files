# ============================================
# User Story #27 - User PIN - View Request View Count
# BCE Structure
# ============================================


# --- Boundary ---
class ViewCountPage:
    def __init__(self, controller=None):
        self.controller = controller or ViewCountController()

    def showViewCount(self, requestID):
        result = self.controller.showViewCount(requestID)
        return result


# --- Controller ---
class ViewCountController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def showViewCount(self, requestID) -> int:
        if not requestID or not str(requestID).strip():
            return "Error: Request ID is required."

        if not self.load_requests:
            return "Error: load_requests function not provided."

        result = self.entity.showViewCount(
            requestID,
            load_requests_func=self.load_requests
        )
        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._viewCount = 0

    def showViewCount(self, requestID, load_requests_func=None) -> int:
        if not load_requests_func:
            return "Error: load_requests function not provided."

        all_requests = load_requests_func()

        for req in all_requests:
            req_id = str(req.get('id', '')).strip()
            if req_id == str(requestID).strip() or req_id.replace('REQ-', '') == str(requestID).strip().replace('REQ-', ''):
                raw_value = req.get('viewCount')
                if raw_value is None:
                    raw_value = req.get('view_count')
                if raw_value is None:
                    raw_value = req.get('views')

                try:
                    self._viewCount = int(raw_value) if raw_value is not None else 0
                except (ValueError, TypeError):
                    self._viewCount = 0

                return self._viewCount

        return f"Error: Request with ID '{requestID}' not found."
