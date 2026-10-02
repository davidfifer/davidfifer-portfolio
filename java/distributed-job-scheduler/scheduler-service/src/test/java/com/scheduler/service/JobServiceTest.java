package com.scheduler.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.scheduler.dto.JobStatusResponse;
import com.scheduler.dto.SubmitJobRequest;
import com.scheduler.dto.SubmitJobResponse;
import com.scheduler.model.Job;
import com.scheduler.model.JobStatus;
import com.scheduler.repository.JobRepository;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.*;

class JobServiceTest {

    @Test
    void submitJob_createsPendingJob() {
        ObjectMapper mapper = mock(ObjectMapper.class);
        JobRepository repo = mock(JobRepository.class);
        JobService jobService = new JobService(mapper, repo);

        SubmitJobRequest request = new SubmitJobRequest();
        request.setPayload("{\"hello\":\"world\"}");
        request.setMaxAttempts(3);

        Job savedJob = new Job();
        savedJob.setId(UUID.randomUUID());
        savedJob.setStatus(JobStatus.PENDING);
        savedJob.setCreatedAt(Instant.now());
        savedJob.setNextRunAt(Instant.now());

        when(repo.save(any(Job.class))).thenReturn(savedJob);

        SubmitJobResponse response = jobService.submitJob(request);

        assertNotNull(response);
        assertEquals(savedJob.getId(), response.id());
        verify(repo).save(any(Job.class));
    }

    @Test
    void getStatus_returnsJobStatusResponse() {
        ObjectMapper mapper = mock(ObjectMapper.class);
        JobRepository repo = mock(JobRepository.class);
        JobService jobService = new JobService(mapper, repo);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.SUCCESS);
        job.setAttempts(0);
        job.setMaxAttempts(3);
        job.setNextRunAt(Instant.now());
        job.setCreatedAt(Instant.now());

        when(repo.findById(job.getId())).thenReturn(Optional.of(job));

        JobStatusResponse response = jobService.getStatus(job.getId());

        assertNotNull(response);
        assertEquals(job.getId(), response.id());
        assertEquals(JobStatus.SUCCESS, response.status());
    }
}
