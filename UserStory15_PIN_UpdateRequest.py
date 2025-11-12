# ============================================
# User Story #15 - User PIN - Update Request
# BCE Structure
# ============================================

from datetime import datetime


# --- Boundary ---
class UpdateRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or UpdateRequestController()

    def updateInfo(self, data):
        result = self.controller.submitUpdate(data)
        return result


# --- Controller ---
class UpdateRequestController:
    def __init__(self, entity=None, load_requests_func=None, save_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func
        self.save_requests = save_requests_func

    def submitUpdate(self, data) -> str:
        # Validate required input
        if not data or not isinstance(data, dict):
            return "Error: Update data is required."
        
        requestID = data.get('requestID') or data.get('id')
        if not requestID:
            return "Error: Request ID is required."
        
        # Load existing requests
        if not self.load_requests:
            return "Error: load_requests function not provided."
        
        all_requests = self.load_requests()
        
        # Find the request by ID
        request_found = None
        request_index = -1
        for idx, req in enumerate(all_requests):
            req_id = str(req.get('id', '')).strip()
            request_id_str = str(requestID).strip()
            
            if req_id == request_id_str or req_id.replace('REQ-', '') == request_id_str.replace('REQ-', ''):
                request_found = req
                request_index = idx
                break
        
        if not request_found:
            return f"Error: Request with ID '{requestID}' not found."
        
        # Delegate to entity
        result = self.entity.submitUpdate(
            request_found,
            data,
            save_requests_func=self.save_requests,
            all_requests=all_requests,
            request_index=request_index
        )
        
        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._requestTitle = None
        self._requestCategory = None
        self._requestStatus = None
        self._requestDescription = None
        self._requestDate = None
        self._requestLocation = None

    def submitUpdate(self, request_data, update_data, save_requests_func=None, all_requests=None, request_index=-1) -> str:
        # Extract update fields from data
        newTitle = update_data.get('title') or update_data.get('requestTitle')
        newCategory = update_data.get('category') or update_data.get('requestCategory')
        newDescription = update_data.get('description') or update_data.get('requestDescription')
        newDate = update_data.get('date') or update_data.get('requestDate')
        newLocation = update_data.get('location') or update_data.get('requestLocation')
        newTime = update_data.get('time')
        newStatus = update_data.get('status') or update_data.get('requestStatus')
        
        # Update entity attributes and request data
        if newTitle is not None:
            self._requestTitle = newTitle
            request_data['title'] = newTitle
        
        if newCategory is not None:
            self._requestCategory = newCategory
            request_data['category'] = newCategory
        
        if newDescription is not None:
            self._requestDescription = newDescription
            request_data['description'] = newDescription
        
        if newDate is not None:
            # Validate date format
            try:
                datetime.strptime(newDate, '%Y-%m-%d')
                self._requestDate = newDate
                request_data['date'] = newDate
            except ValueError:
                return "Error: Invalid date format. Please use YYYY-MM-DD."
        
        if newLocation is not None:
            self._requestLocation = newLocation
            request_data['location'] = newLocation
        
        if newTime is not None:
            # Validate time format
            try:
                datetime.strptime(newTime, '%H:%M')
                request_data['time'] = newTime
            except ValueError:
                return "Error: Invalid time format. Please use HH:MM."
        
        if newStatus is not None:
            self._requestStatus = newStatus
            request_data['status'] = newStatus
        
        # Update last_updated timestamp
        request_data['last_updated'] = datetime.now().isoformat()
        
        # Save updated requests
        if save_requests_func and all_requests is not None:
            try:
                save_requests_func(all_requests)
                return request_data
            except Exception as e:
                return f"Error saving updated request: {str(e)}"
        else:
            return "Error: save_requests function not provided."

