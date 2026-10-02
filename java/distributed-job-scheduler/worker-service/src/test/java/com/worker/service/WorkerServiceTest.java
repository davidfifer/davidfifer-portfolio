package com.worker.service;

import com.worker.model.Job;
import com.worker.model.JobStatus;
import com.worker.repository.JobRepository;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class WorkerServiceTest {

    @Test
    void claimNextJob_marksJobRunningAndReturnsIt() {
        JobRepository repo = mock(JobRepository.class);
        WorkerService workerService = new WorkerService(repo);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.PENDING);
        job.setNextRunAt(Instant.now());

        when(repo.findNextRunnableJob(eq(JobStatus.PENDING), any(Instant.class)))
                .thenReturn(Optional.of(job));

        when(repo.save(any(Job.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Job claimed = workerService.claimNextJob();

        assertNotNull(claimed);
        assertEquals(JobStatus.RUNNING, claimed.getStatus());
        verify(repo).save(claimed);
    }

    @Test
    void execute_marksJobSuccess() {
        JobRepository repo = mock(JobRepository.class);
        WorkerService workerService = new WorkerService(repo);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.RUNNING);

        workerService.execute(job);

        assertEquals(JobStatus.SUCCESS, job.getStatus());
        verify(repo).save(job);
    }
}
