package com.notesapi.exceptions;

import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;
import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(NotFoundException ex, HttpServletRequest request) {
        log.warn("NotFoundException: {}", ex.getMessage());
        return buildResponse(ex.getMessage(), "NotFoundException", HttpStatus.NOT_FOUND, request);
    }

    @ExceptionHandler(InvalidCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleInvalidCredentials(InvalidCredentialsException ex,
                                                                  HttpServletRequest request) {
        log.warn("InvalidCredentialsException: {}", ex.getMessage());
        return buildResponse(ex.getMessage(), "InvalidCredentialsException", HttpStatus.UNAUTHORIZED, request);
    }

    @ExceptionHandler(DuplicateEmailException.class)
    public ResponseEntity<ErrorResponse> handleDuplicateEmail(DuplicateEmailException ex, HttpServletRequest request) {
        log.warn("DuplicateEmailException: {}", ex.getMessage());
        return buildResponse(ex.getMessage(), "DuplicateEmailException", HttpStatus.BAD_REQUEST, request);
    }

    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidation(ValidationException ex, HttpServletRequest request) {
        log.warn("ValidationException: {}", ex.getMessage());
        return buildResponse(ex.getMessage(), "ValidationException", HttpStatus.UNPROCESSABLE_ENTITY, request);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex,
                                                                HttpServletRequest request) {
        String message = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(err -> err.getField() + ": " + err.getDefaultMessage())
                .collect(Collectors.joining(", "));

        log.warn("Validation errors: {}", message);

        return buildResponse(message, "ValidationException", HttpStatus.UNPROCESSABLE_ENTITY, request);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception ex, HttpServletRequest request) {
        log.error("Unexpected error", ex);
        return buildResponse("An unexpected error occurred", "Exception",
                HttpStatus.INTERNAL_SERVER_ERROR, request);
    }

    private ResponseEntity<ErrorResponse> buildResponse(String message, String error, HttpStatus status,
                                                        HttpServletRequest request) {
        ErrorResponse response = ErrorResponse.builder()
                .error(error)
                .message(message)
                .status(status.value())
                .timestamp(Instant.now())
                .path(request.getRequestURI())
                .build();

        return new ResponseEntity<>(response, status);
    }
}
