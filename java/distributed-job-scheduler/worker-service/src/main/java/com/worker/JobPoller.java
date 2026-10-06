package com.worker;

import com.worker.model.Job;
import com.worker.service.WorkerService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class JobPoller {

    private final WorkerService workerService;
    private static final Logger logger = LoggerFactory.getLogger(JobPoller.class);

    public JobPoller(WorkerService workerService) {
        this.workerService = workerService;
    }

    @Scheduled(fixedDelay = 1000)
    public void poll() {
        logger.info("Polling for jobs...");
        boolean keepPolling = true;

        try {
            while (keepPolling) {
                Job job =  workerService.claimNextJob();

                if (job == null) {
                    logger.info("No runnable jobs found");
                    Thread.sleep(1000);
                    return;
                }

                logger.info("Executing job id={}", job.getId());
                workerService.execute(job);
                keepPolling = false;
            }
        } catch (InterruptedException e) {
            logger.error("Pooling loop interrupted: {}", e.getMessage());
            Thread.currentThread().interrupt();
            throw new RuntimeException(e);
        }
    }
}
