# ============================================
# User Story #23 - User CSR Rep - Search Shortlist
# BCE Structure
# ============================================


# --- Boundary ---
class SearchSLRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or SearchSLRequestController()

    def submitSearch(self, shortlisted=True, data=None) -> str:
        result = self.controller.searchRequest(shortlisted=shortlisted, data=data)
        return result


# --- Controller ---
class SearchSLRequestController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def searchRequest(self, shortlisted=True, data=None) -> str:
        # Validate input
        if data is None:
            data = {}
        if not isinstance(data, dict):
            return "Error: Search data must be a dictionary."

        if shortlisted is None:
            shortlisted = True

        # Load existing requests
        if not self.load_requests:
            return "Error: load_requests function not provided."

        all_requests = self.load_requests()

        # Delegate to entity
        result = self.entity.searchRequest(
            shortlisted=shortlisted,
            data=data,
            all_requests=all_requests
        )

        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._requestID = None
        self._requestTitle = None
        self._requestCategory = None
        self._requestDate = None
        self._requestStatus = None
        self._shortlisted = False

    def _is_shortlisted(self, req) -> bool:
        flag_keys = ['shortlisted', 'is_shortlisted', 'favorite', 'is_favorite']
        for key in flag_keys:
            value = req.get(key)
            if isinstance(value, bool) and value:
                return True

        status = str(req.get('status', '')).lower()
        if status == 'shortlisted':
            return True

        list_keys = ['shortlisted_by', 'favorites', 'shortlist']
        for key in list_keys:
            value = req.get(key)
            if isinstance(value, list) and len(value) > 0:
                return True
            if isinstance(value, str) and value.strip():
                return True

        return False

    def searchRequest(self, shortlisted=True, data=None, all_requests=None) -> str:
        if data is None:
            data = {}

        if all_requests is None:
            all_requests = []

        searchID = data.get('id') or data.get('requestID')
        searchTitle = data.get('title') or data.get('requestTitle')
        searchCategory = data.get('category') or data.get('requestCategory')
        searchDate = data.get('date') or data.get('requestDate')
        searchStatus = data.get('status') or data.get('requestStatus')
        searchKeyword = data.get('keyword') or data.get('search')

        matched_requests = []

        for req in all_requests:
            is_shortlisted = self._is_shortlisted(req)
            if shortlisted and not is_shortlisted:
                continue

            match = True

            if searchID:
                req_id = str(req.get('id', '')).strip()
                search_id_str = str(searchID).strip()
                if not (req_id == search_id_str or req_id.replace('REQ-', '') == search_id_str.replace('REQ-', '')):
                    match = False

            if match and searchTitle:
                req_title = str(req.get('title', '')).lower()
                if str(searchTitle).lower() not in req_title:
                    match = False

            if match and searchCategory:
                req_category = str(req.get('category', '')).lower()
                if str(searchCategory).lower() not in req_category:
                    match = False

            if match and searchDate:
                req_date = str(req.get('date', '')).strip()
                if str(searchDate).strip() not in req_date:
                    match = False

            if match and searchStatus:
                req_status = str(req.get('status', '')).lower()
                if str(searchStatus).lower() not in req_status:
                    match = False

            if match and searchKeyword:
                keyword = str(searchKeyword).lower()
                req_title = str(req.get('title', '')).lower()
                req_description = str(req.get('description', '')).lower()
                req_category = str(req.get('category', '')).lower()

                if keyword not in req_title and keyword not in req_description and keyword not in req_category:
                    match = False

            if match:
                matched_requests.append(req)

        return matched_requests
