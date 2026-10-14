package com.worker.poller;

import com.worker.model.Job;
import com.worker.service.WorkerService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
public class JobPoller {

    @Value("${WORKER_ID:unknown}")
    private String workerId = "unknown";

    private final WorkerService workerService;
    private static final Logger logger = LoggerFactory.getLogger(JobPoller.class);

    public JobPoller(WorkerService workerService) {
        this.workerService = workerService;
    }

    @Scheduled(fixedDelay = 10000)
    public void poll() {
        logger.info("[{}] Polling for jobs...", workerId);

        Optional<Job> jobOpt = workerService.claimNextJob();

        if (jobOpt.isEmpty()) {
            logger.info("[{}] No runnable jobs found", workerId);
            return;
        }

        Job job = jobOpt.get();
        workerService.execute(job);
    }
}
