# ============================================
# User Story #13 - User PIN - Create Request
# BCE Structure
# ============================================

from datetime import datetime


# --- Boundary ---
class CreateRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or CreateRequestController()

    def submitCreateRequest(self, requestTitle, requestDescription, requestCategory, requestDate, requestLocation,
                           owner=None, time=None, request_id=None):

        result = self.controller.createRequest(
            requestTitle, 
            requestDescription, 
            requestCategory, 
            requestDate, 
            requestLocation,
            owner=owner,
            time=time,
            request_id=request_id
        )
        return result


# --- Controller ---
class CreateRequestController:
    def __init__(self, entity=None, load_requests_func=None, save_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func
        self.save_requests = save_requests_func

    def createRequest(self, requestTitle, requestDescription, requestCategory, requestDate, requestLocation, 
                     owner=None, time=None, request_id=None) -> str:

        # Validate required inputs
        if not requestTitle or not requestTitle.strip():
            return "Error: Request title is required."
        if not requestDescription or not requestDescription.strip():
            return "Error: Request description is required."
        if not requestCategory or not requestCategory.strip():
            return "Error: Request category is required."
        if not requestDate or not requestDate.strip():
            return "Error: Request date is required."
        if not requestLocation or not requestLocation.strip():
            return "Error: Request location is required."
        
        # Delegate to entity
        result = self.entity.createRequest(
            requestTitle, 
            requestDescription, 
            requestCategory, 
            requestDate, 
            requestLocation,
            load_requests_func=self.load_requests,
            save_requests_func=self.save_requests,
            owner=owner,
            time=time,
            request_id=request_id
        )
        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._requestID = None
        self._requestTitle = None
        self._requestCategory = None
        self._requestDescription = None
        self._requestDate = None
        self._requestLocation = None

    def createRequest(self, requestTitle, requestDescription, requestCategory, requestDate, requestLocation, 
                     load_requests_func=None, save_requests_func=None, owner=None, time=None, request_id=None) -> str:

        # Set entity attributes
        self._requestTitle = requestTitle
        self._requestDescription = requestDescription
        self._requestCategory = requestCategory
        self._requestDate = requestDate
        self._requestLocation = requestLocation
        
        # Load existing requests
        if load_requests_func:
            all_requests = load_requests_func()
        else:
            return "Error: load_requests function not provided."
        
        # Generate new request ID
        if request_id:
            self._requestID = request_id
        else:
            self._requestID = len(all_requests) + 100
        
        # Create request object
        new_request = {
            'id': request_id if request_id else f'REQ-{self._requestID}',
            'title': self._requestTitle,
            'category': self._requestCategory,
            'description': self._requestDescription,
            'location': self._requestLocation,
            'date': self._requestDate,
            'time': time or '',
            'status': 'Pending',
            'owner': owner or '',
            'created': datetime.now().isoformat()
        }
        
        # Save to storage
        if save_requests_func:
            all_requests.append(new_request)
            try:
                save_requests_func(all_requests)
                return new_request
            except Exception as e:
                return f"Error saving request: {str(e)}"
        else:
            return "Error: save_requests function not provided."

