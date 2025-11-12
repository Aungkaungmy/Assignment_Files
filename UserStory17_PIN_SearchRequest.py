# ============================================
# User Story #17 - User PIN - Search Request
# BCE Structure
# ============================================


# --- Boundary ---
class SearchRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or SearchRequestController()

    def submitSearch(self, data) -> str:
        result = self.controller.searchRequest(data)
        return result


# --- Controller ---
class SearchRequestController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func

    def searchRequest(self, data) -> str:
        # Validate input (allow empty dict to return all requests)
        if data is None or not isinstance(data, dict):
            return "Error: Search data must be a dictionary."
        
        # Load existing requests
        if not self.load_requests:
            return "Error: load_requests function not provided."
        
        all_requests = self.load_requests()
        
        # Delegate to entity
        result = self.entity.searchRequest(
            data,
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

    def searchRequest(self, data, all_requests=None) -> str:
        # Extract search criteria
        searchID = data.get('id') or data.get('requestID')
        searchTitle = data.get('title') or data.get('requestTitle')
        searchCategory = data.get('category') or data.get('requestCategory')
        searchDate = data.get('date') or data.get('requestDate')
        searchStatus = data.get('status') or data.get('requestStatus')
        searchKeyword = data.get('keyword') or data.get('search')
        
        # If no search criteria provided, return all requests
        if not any([searchID, searchTitle, searchCategory, searchDate, searchStatus, searchKeyword]):
            if all_requests:
                return all_requests
            else:
                return []
        
        # Filter requests based on search criteria
        matched_requests = []
        
        for req in all_requests or []:
            match = True
            
            # Search by ID
            if searchID:
                req_id = str(req.get('id', '')).strip()
                search_id_str = str(searchID).strip()
                if not (req_id == search_id_str or req_id.replace('REQ-', '') == search_id_str.replace('REQ-', '')):
                    match = False
            
            # Search by title
            if match and searchTitle:
                req_title = str(req.get('title', '')).lower()
                search_title_str = str(searchTitle).lower()
                if search_title_str not in req_title:
                    match = False
            
            # Search by category
            if match and searchCategory:
                req_category = str(req.get('category', '')).lower()
                search_category_str = str(searchCategory).lower()
                if search_category_str not in req_category:
                    match = False
            
            # Search by date
            if match and searchDate:
                req_date = str(req.get('date', '')).strip()
                search_date_str = str(searchDate).strip()
                if search_date_str not in req_date:
                    match = False
            
            # Search by status
            if match and searchStatus:
                req_status = str(req.get('status', '')).lower()
                search_status_str = str(searchStatus).lower()
                if search_status_str not in req_status:
                    match = False
            
            # Search by keyword (searches in title, description, category)
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

