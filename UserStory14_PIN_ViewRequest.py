# ============================================
# User Story #14 - User PIN - View Request
# BCE Structure
# ============================================


# --- Boundary ---
class ViewRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or ViewRequestController()

    def getRequestDetail(self, requestID):
        result = self.controller.getRequestDetail(requestID)
        return result


# --- Controller ---
class ViewRequestController:
    def __init__(self, entity=None, load_requests_func=None):
        self.entity = entity or ViewRequestEntity()
        self.load_requests = load_requests_func

    def getRequestDetail(self, requestID) -> str:
        # Validate required input
        if not requestID or not str(requestID).strip():
            return "Error: Request ID is required."
        
        # Delegate to entity
        result = self.entity.getRequestDetail(
            requestID,
            load_requests_func=self.load_requests
        )
        return result


# --- Entity ---
class ViewRequestEntity:
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

    def getRequestDetail(self, requestID, load_requests_func=None) -> str:

        # Load requests from storage
        if load_requests_func:
            all_requests = load_requests_func()
        else:
            return "Error: load_requests function not provided."
        
        # Find the request by ID
        request_found = None
        for req in all_requests:
            
            req_id = str(req.get('id', '')).strip()
            request_id_str = str(requestID).strip()
            
           
            if req_id == request_id_str or req_id.replace('REQ-', '') == request_id_str.replace('REQ-', ''):
                request_found = req
                break
        
        if not request_found:
            return f"Error: Request with ID '{requestID}' not found."
        
        
        self._requestID = request_found.get('id')
        self._requestTitle = request_found.get('title', '')
        self._requestCategory = request_found.get('category', '')
        self._requestStatus = request_found.get('status', 'Pending')
        self._requestDescription = request_found.get('description', '')
        self._requestDate = request_found.get('date', '')
        self._requestLocation = request_found.get('location', '')
        self._PIN = request_found.get('owner', '')
        self._CSRRepInCharge = request_found.get('assignee') or request_found.get('csr') or ''
        
    
        request_detail = {
            'id': self._requestID,
            'title': self._requestTitle,
            'category': self._requestCategory,
            'status': self._requestStatus,
            'description': self._requestDescription,
            'date': self._requestDate,
            'time': request_found.get('time', ''),
            'location': self._requestLocation,
            'owner': self._PIN,
            'assignee': self._CSRRepInCharge,
            'created': request_found.get('created', ''),
            'csr': self._CSRRepInCharge
        }
        
        return request_detail

