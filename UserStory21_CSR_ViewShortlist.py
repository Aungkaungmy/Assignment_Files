# ============================================
# User Story #21 - User CSR Rep - View Shortlist
# BCE Structure
# ============================================


# --- Boundary ---
class ViewShortlistPage:
    def __init__(self, controller=None):
        self.controller = controller or ViewShortlistController()

    def getShortlist(self):
        result = self.controller.getShortlist()
        return result


# --- Controller ---
class ViewShortlistController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def getShortlist(self) -> str:
        # Load shortlisted requests via entity
        result = self.entity.getShortlist(load_requests_func=self.load_requests)
        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._requestID = None

    def getShortlist(self, load_requests_func=None) -> str:
        # Load requests from storage
        if load_requests_func:
            all_requests = load_requests_func()
        else:
            return "Error: load_requests function not provided."

        shortlisted_requests = []

        for req in all_requests or []:
            req_id = req.get('id')
            is_shortlisted = False

            # Detect shortlisted flags
            flag_keys = ['shortlisted', 'is_shortlisted', 'favorite', 'is_favorite']
            for key in flag_keys:
                value = req.get(key)
                if isinstance(value, bool) and value:
                    is_shortlisted = True
                    break

            # Status-based detection
            if not is_shortlisted:
                status = str(req.get('status', '')).lower()
                if status == 'shortlisted':
                    is_shortlisted = True

            # List/string based detection (e.g., shortlist owners)
            if not is_shortlisted:
                list_keys = ['shortlisted_by', 'favorites', 'shortlist']
                for key in list_keys:
                    value = req.get(key)
                    if isinstance(value, list) and len(value) > 0:
                        is_shortlisted = True
                        break
                    if isinstance(value, str) and value.strip():
                        is_shortlisted = True
                        break

            if is_shortlisted:
                shortlisted_requests.append({
                    'id': req_id,
                    'title': req.get('title'),
                    'category': req.get('category'),
                    'status': req.get('status'),
                    'description': req.get('description'),
                    'date': req.get('date'),
                    'time': req.get('time', ''),
                    'location': req.get('location'),
                    'owner': req.get('owner'),
                    'assignee': req.get('assignee'),
                    'created': req.get('created'),
                })

        return shortlisted_requests
