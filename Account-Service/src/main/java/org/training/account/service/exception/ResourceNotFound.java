package org.training.account.service.exception;

public class ResourceNotFound extends GlobalException{

    public ResourceNotFound() {
        super(GlobalErrorCode.NOT_FOUND, "Resource not found on the server");
    }

    public ResourceNotFound(String message) {
        super(GlobalErrorCode.NOT_FOUND, message);
    }
}
