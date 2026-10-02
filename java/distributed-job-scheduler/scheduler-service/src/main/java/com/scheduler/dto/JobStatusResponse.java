package com.scheduler.dto;

import com.scheduler.model.JobStatus;

import java.time.Instant;
import java.util.UUID;

public record JobStatusResponse(
        UUID id,
        JobStatus status,
        int attempts,
        int maxAttempts,
        Instant nextRunAt,
        Instant createdAt
) {}
