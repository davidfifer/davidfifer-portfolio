package com.scheduler.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.scheduler.dto.JobStatusResponse;
import com.scheduler.dto.SubmitJobRequest;
import com.scheduler.dto.SubmitJobResponse;
import com.scheduler.exception.JobNotFoundException;
import com.scheduler.model.Job;
import com.scheduler.model.JobStatus;
import com.scheduler.repository.JobRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.UUID;

@Service
public class JobService {

    private final ObjectMapper objectMapper;
    private final JobRepository jobRepository;

    private static final Logger logger = LoggerFactory.getLogger(JobService.class);

    public JobService(ObjectMapper objectMapper, JobRepository jobRepository) {
        this.objectMapper = objectMapper;
        this.jobRepository = jobRepository;
    }

    public SubmitJobResponse submitJob(SubmitJobRequest request) {

        // Validate payload
        if (request.getPayload() == null || request.getPayload().isBlank()) {
            logger.error("Validation failed: empty payload");
            throw new IllegalArgumentException("Payload cannot be empty");
        }

        // Validate JSON
        try {
            objectMapper.readTree(request.getPayload());
        } catch (Exception e) {
            logger.error("Validation failed: payload invalid JSON, error={}", e.getMessage());
            throw new IllegalArgumentException("Payload must be valid JSON");
        }

        // Initialize job fields
        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setPayload(request.getPayload());
        job.setStatus(JobStatus.PENDING);
        job.setAttempts(0);
        job.setMaxAttempts(request.getMaxAttempts());
        job.setCreatedAt(Instant.now());
        job.setNextRunAt(Instant.now());

        // Persist job
        Job saved = jobRepository.save(job);
        UUID jobId = saved.getId();

        logger.info("Job submitted: id={}, status={}", jobId, saved.getStatus());

        // Return ID
        return new SubmitJobResponse(jobId);
    }

    public JobStatusResponse getStatus(UUID id) {

        Job job = jobRepository.findById(id)
                .orElseThrow(() -> new JobNotFoundException(id));

        return new JobStatusResponse(
                job.getId(),
                job.getStatus(),
                job.getAttempts(),
                job.getMaxAttempts(),
                job.getNextRunAt(),
                job.getCreatedAt()
        );
    }
}
