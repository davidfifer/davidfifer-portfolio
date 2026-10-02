package com.worker;

import com.worker.model.Job;
import com.worker.service.WorkerService;
import org.junit.jupiter.api.Test;

import static org.mockito.Mockito.*;

class JobPollerTest {

    @Test
    void poll_doesNothingWhenNoJobFound() {
        WorkerService workerService = mock(WorkerService.class);
        JobPoller poller = new JobPoller(workerService);

        when(workerService.claimNextJob()).thenReturn(null);

        poller.poll();

        verify(workerService, never()).execute(any());
    }

    @Test
    void poll_executesJobWhenFound() {
        WorkerService workerService = mock(WorkerService.class);
        JobPoller poller = new JobPoller(workerService);

        Job job = new Job();
        when(workerService.claimNextJob()).thenReturn(job);

        poller.poll();

        verify(workerService).execute(job);
    }
}
