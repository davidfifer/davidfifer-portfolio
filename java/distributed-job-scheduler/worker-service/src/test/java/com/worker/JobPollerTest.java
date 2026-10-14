package com.worker;

import com.worker.model.Job;
import com.worker.poller.JobPoller;
import com.worker.service.WorkerService;
import org.junit.jupiter.api.Test;

import java.util.Optional;
import java.util.UUID;

import static org.mockito.Mockito.*;

class JobPollerTest {

    @Test
    void poll_doesNothingWhenNoJobFound() {
        WorkerService workerService = mock(WorkerService.class);
        JobPoller poller = new JobPoller(workerService);

        when(workerService.claimNextJob()).thenReturn(Optional.empty());

        poller.poll();

        verify(workerService, never()).execute(any());
    }

    @Test
    void poll_executesJobWhenFound() {
        WorkerService workerService = mock(WorkerService.class);
        JobPoller poller = new JobPoller(workerService);

        Job job = new Job();
        job.setId(UUID.randomUUID());
        when(workerService.claimNextJob()).thenReturn(Optional.of(job));

        poller.poll();

        verify(workerService).execute(job);
    }
}
