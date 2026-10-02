package com.scheduler.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    private static final Logger logger = LoggerFactory.getLogger(ApiExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<?> handleValidation(MethodArgumentNotValidException ex) {

        String message = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(FieldError::getDefaultMessage)
                .findFirst()
                .orElse("Invalid request");

        logger.error("Validation failed: field={}, message={}",
                ex.getBindingResult().getFieldErrors().get(0).getField(),
                message);

        return ResponseEntity.badRequest().body(message);
    }

    @ExceptionHandler(JobNotFoundException.class)
    public ResponseEntity<?> handleJobNotFound(JobNotFoundException ex) {

        logger.error("Job not found: {}", ex.getMessage());

        return ResponseEntity.status(404).body(ex.getMessage());
    }
}
