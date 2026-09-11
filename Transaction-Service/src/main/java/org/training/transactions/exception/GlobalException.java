package org.training.transactions.exception;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Data
@EqualsAndHashCode(callSuper = true)
@AllArgsConstructor
@NoArgsConstructor
public class GlobalException extends RuntimeException {

    private String errorCode;

    private String message;

    public GlobalException(String message) {
        this.message = message;
    }
}
