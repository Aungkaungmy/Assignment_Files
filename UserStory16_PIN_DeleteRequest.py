# ============================================
# User Story #16 - User PIN - Delete Request
# BCE Structure
# ============================================


# --- Boundary ---
class DeleteRequestPage:
    def __init__(self, controller=None):
        self.controller = controller or DeleteRequestController()

    def deleteConfirm(self, requestID=None) -> str:
        result = self.controller.deleteRequest(requestID)
        return result

    def deleteRequest(self, requestID=None) -> str:
        result = self.controller.deleteRequest(requestID)
        return result


# --- Controller ---
class DeleteRequestController:
    def __init__(self, entity=None, load_requests_func=None, save_requests_func=None):
        self.entity = entity or Request()
        self.load_requests = load_requests_func
        self.save_requests = save_requests_func

    def deleteRequest(self, requestID) -> str:
        # Validate required input
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
        result = self.entity.deleteRequest(
            requestID,
            save_requests_func=self.save_requests,
            all_requests=all_requests,
            request_index=request_index
        )
        
        return result


# --- Entity ---
class Request:
    def __init__(self):
        self._requestID = None

    def deleteRequest(self, requestID, save_requests_func=None, all_requests=None, request_index=-1) -> str:
        # Set entity attribute
        self._requestID = requestID
        
        # Remove request from list
        if all_requests is not None and request_index >= 0:
            deleted_request = all_requests.pop(request_index)
            
            # Save updated requests
            if save_requests_func:
                try:
                    save_requests_func(all_requests)
                    return f"Request '{requestID}' deleted successfully."
                except Exception as e:
                    return f"Error saving after deletion: {str(e)}"
            else:
                return "Error: save_requests function not provided."
        else:
            return "Error: Unable to delete request."

