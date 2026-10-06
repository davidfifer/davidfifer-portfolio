package com.worker.service;

import com.worker.executor.WorkExecutor;
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
        WorkExecutor executor = mock(WorkExecutor.class);
        WorkerService workerService = new WorkerService(repo, executor);

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
        WorkExecutor executor = mock(WorkExecutor.class);
        WorkerService workerService = new WorkerService(repo, executor);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.RUNNING);

        when(repo.findById(job.getId())).thenReturn(Optional.of(job));

        workerService.execute(job);

        assertEquals(JobStatus.SUCCESS, job.getStatus());
        verify(repo).save(job);
    }

    @Test
    void execute_retriesJobAndSchedulesBackoff() throws Exception {
        JobRepository repo = mock(JobRepository.class);
        WorkExecutor executor = mock(WorkExecutor.class);
        WorkerService workerService = new WorkerService(repo, executor);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.RUNNING);
        job.setAttempts(0);
        job.setMaxAttempts(5);

        when(repo.findById(job.getId())).thenReturn(Optional.of(job));

        doThrow(new RuntimeException("boom"))
                .when(executor).execute(any(Job.class));

        workerService.execute(job);   // <-- NO assertThrows

        assertEquals(JobStatus.PENDING, job.getStatus());
        assertEquals(1, job.getAttempts());
        assertNotNull(job.getNextRunAt());
    }

    @Test
    void execute_marksJobFailedPermanentlyAfterMaxAttempts() throws Exception {
        JobRepository repo = mock(JobRepository.class);
        WorkExecutor executor = mock(WorkExecutor.class);

        WorkerService workerService = new WorkerService(repo, executor);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.RUNNING);
        job.setAttempts(5);
        job.setMaxAttempts(5);

        // Return a fresh RUNNING job from the database
        Job dbJob = new Job();
        dbJob.setId(job.getId());
        dbJob.setStatus(JobStatus.RUNNING);
        dbJob.setAttempts(5);
        dbJob.setMaxAttempts(5);

        when(repo.findById(job.getId())).thenReturn(Optional.of(dbJob));

        doThrow(new RuntimeException("boom"))
                .when(executor).execute(any(Job.class));

        workerService.execute(job);

        assertEquals(JobStatus.FAILED, job.getStatus());
        assertEquals(6, job.getAttempts());
        assertNull(job.getNextRunAt());
    }

    @Test
    void execute_doesNothingIfJobIsNotRunnable() {
        JobRepository repo = mock(JobRepository.class);
        WorkExecutor executor = mock(WorkExecutor.class);
        WorkerService workerService = new WorkerService(repo, executor);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        job.setStatus(JobStatus.RUNNING);

        Job dbJob = new Job();
        dbJob.setStatus(JobStatus.SUCCESS);

        when(repo.findById(job.getId())).thenReturn(Optional.of(dbJob));

        workerService.execute(job);

        verify(repo, never()).save(any());
    }
}
