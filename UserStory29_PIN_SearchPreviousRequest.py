# ============================================
# User Story #29 - User PIN - Search Previous Request
# BCE Structure
# ============================================


# --- Boundary ---
class SearchPrevRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or SearchPrevRequestController()

    def submitSearch(self, requestStatus='Completed', filterCriteria=None, data=None) -> str:
        return self.controller.searchRequest(
            requestStatus=requestStatus,
            filterCriteria=filterCriteria,
            data=data
        )


# --- Controller ---
class SearchPrevRequestController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def searchRequest(self, requestStatus='Completed', filterCriteria=None, data=None) -> str:
        if data is None:
            data = {}
        if filterCriteria is None:
            filterCriteria = {}

        if not isinstance(data, dict) or not isinstance(filterCriteria, dict):
            return "Error: search data must be dictionaries."

        if not requestStatus:
            requestStatus = 'Completed'

        if not self.load_requests:
            return "Error: load_requests function not provided."

        all_requests = self.load_requests()

        return self.entity.searchRequest(
            requestStatus=requestStatus,
            filterCriteria=filterCriteria,
            data=data,
            all_requests=all_requests
        )


# --- Entity ---
class Request:
    def __init__(self):
        self._requestID = None
        self._requestTitle = None
        self._requestCategory = None
        self._requestDate = None
        self._requestStatus = None

    def _matches_filters(self, req, filters):
        for key, expected in (filters or {}).items():
            value = req.get(key)
            if isinstance(expected, str):
                if str(expected).lower() not in str(value or '').lower():
                    return False
            else:
                if value != expected:
                    return False
        return True

    def searchRequest(self, requestStatus='Completed', filterCriteria=None, data=None, all_requests=None) -> str:
        if filterCriteria is None:
            filterCriteria = {}
        if data is None:
            data = {}
        if all_requests is None:
            all_requests = []

        keyword = data.get('keyword') or data.get('search')
        searchCategory = data.get('category')
        searchDate = data.get('date')

        matched_requests = []

        for req in all_requests:
            status = str(req.get('status', '')).lower()
            target_status = str(requestStatus).lower()
            if target_status and status != target_status:
                continue

            if not self._matches_filters(req, filterCriteria):
                continue

            if keyword:
                kw = str(keyword).lower()
                if (
                    kw not in str(req.get('title', '')).lower()
                    and kw not in str(req.get('description', '')).lower()
                    and kw not in str(req.get('location', '')).lower()
                ):
                    continue

            if searchCategory:
                if str(searchCategory).lower() not in str(req.get('category', '')).lower():
                    continue

            if searchDate:
                if str(searchDate).strip() not in str(req.get('date', '')).strip():
                    continue

            matched_requests.append(req)

        return matched_requests
