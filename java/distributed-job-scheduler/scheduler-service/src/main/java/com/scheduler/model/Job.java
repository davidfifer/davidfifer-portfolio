package com.scheduler.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "job")
public class Job {

    @Id
    private UUID id;

    @Column(columnDefinition = "jsonb")
    private String payload;

    @Enumerated(EnumType.STRING)
    private JobStatus status;

    private int attempts;
    private int maxAttempts;

    private LocalDateTime nextRunAt;
    private LocalDateTime createdAt;
}
