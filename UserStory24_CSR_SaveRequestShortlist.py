# ============================================
# User Story #24 - User CSR Rep - Save Request to Shortlist
# BCE Structure
# ============================================


# --- Boundary ---
class SaveRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or SaveRequestSLController()

    def saveRequestSL(self, requestID):
        result = self.controller.saveRequestSL(requestID)
        return result


# --- Controller ---
class SaveRequestSLController:
    def __init__(self, entity=None, load_requests_func=None, save_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func
        self.save_requests = save_requests_func

    def saveRequestSL(self, requestID) -> str:
        if not requestID or not str(requestID).strip():
            return "Error: Request ID is required."

        if not self.load_requests:
            return "Error: load_requests function not provided."
        if not self.save_requests:
            return "Error: save_requests function not provided."

        all_requests = self.load_requests()

        result = self.entity.saveRequestSL(
            requestID,
            all_requests=all_requests,
            save_requests_func=self.save_requests
        )
        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._requestID = None

    def saveRequestSL(self, requestID, all_requests=None, save_requests_func=None) -> str:
        if all_requests is None:
            all_requests = []

        request_found = None
        for req in all_requests:
            req_id = str(req.get('id', '')).strip()
            if req_id == str(requestID).strip() or req_id.replace('REQ-', '') == str(requestID).strip().replace('REQ-', ''):
                request_found = req
                break

        if not request_found:
            return f"Error: Request with ID '{requestID}' not found."

        flag_keys = ['shortlisted', 'is_shortlisted', 'favorite', 'is_favorite']
        list_keys = ['shortlisted_by', 'favorites', 'shortlist']

        already_shortlisted = False

        for key in flag_keys:
            value = request_found.get(key)
            if isinstance(value, bool) and value:
                already_shortlisted = True
                break

        if not already_shortlisted:
            status = str(request_found.get('status', '')).lower()
            if status == 'shortlisted':
                already_shortlisted = True

        if not already_shortlisted:
            for key in list_keys:
                value = request_found.get(key)
                if isinstance(value, list) and len(value) > 0:
                    already_shortlisted = True
                    break
                if isinstance(value, str) and value.strip():
                    already_shortlisted = True
                    break

        if already_shortlisted:
            return f"Error: Request '{requestID}' is already shortlisted."

        request_found['shortlisted'] = True

        if 'shortlisted_by' in request_found:
            value = request_found['shortlisted_by']
            if isinstance(value, list):
                if 'CSR_Rep' not in value:
                    value.append('CSR_Rep')
                request_found['shortlisted_by'] = value
            elif isinstance(value, str) and value.strip():
                current = [v.strip() for v in value.split(',') if v.strip()]
                if 'CSR_Rep' not in current:
                    current.append('CSR_Rep')
                request_found['shortlisted_by'] = current
            else:
                request_found['shortlisted_by'] = ['CSR_Rep']
        else:
            request_found['shortlisted_by'] = ['CSR_Rep']

        request_found['status'] = request_found.get('status') or 'Shortlisted'

        self._requestID = requestID

        if save_requests_func:
            try:
                save_requests_func(all_requests)
                return f"Request '{requestID}' saved to shortlist successfully."
            except Exception as e:
                return f"Error saving shortlist update: {str(e)}"

        return "Error: save_requests function not provided."
