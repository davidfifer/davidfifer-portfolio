package com.notesapi.exceptions;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data
@Builder
public class ErrorResponse {
    private String error;
    private String message;
    private int status;
    private Instant timestamp;
    private String path;
}
