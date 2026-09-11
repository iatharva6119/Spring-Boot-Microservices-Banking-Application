package org.training.account.service.exception;

public class AccountStatusException extends GlobalException {
    public AccountStatusException(String errorMessage) {
        super(GlobalErrorCode.BAD_REQUEST, errorMessage);
    }
}
