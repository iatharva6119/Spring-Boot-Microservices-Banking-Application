package org.training.account.service.exception;

public class ResourceConflict extends GlobalException{

    public ResourceConflict() {
        super(GlobalErrorCode.CONFLICT, "Account already exists");
    }

    public ResourceConflict(String message) {
        super(GlobalErrorCode.CONFLICT, message);
    }
}
