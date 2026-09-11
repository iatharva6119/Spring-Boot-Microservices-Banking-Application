package org.training.user.service.exception;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Data
@EqualsAndHashCode(callSuper = true)
@AllArgsConstructor
@NoArgsConstructor
public class GlobalException extends RuntimeException{

    private String message;

    private String errorCode;

    public GlobalException(String message) {
        this.message = message;
    }
}
