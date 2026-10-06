package com.worker.service;

import com.worker.executor.WorkExecutor;
import com.worker.model.Job;
import com.worker.model.JobStatus;
import com.worker.repository.JobRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.UUID;

@Service
public class WorkerService {

    private final JobRepository jobRepository;
    private final WorkExecutor workExecutor;

    private static final Logger logger = LoggerFactory.getLogger(WorkerService.class);

    public WorkerService(JobRepository jobRepository, WorkExecutor workExecutor) {
        this.jobRepository = jobRepository;
        this.workExecutor = workExecutor;
    }

    public Job claimNextJob() {
        var jobOpt = jobRepository.findNextRunnableJob(JobStatus.PENDING, Instant.now());

        if (jobOpt.isEmpty()) {
            return null;
        }

        Job job = jobOpt.get();
        job.setStatus(JobStatus.RUNNING);

        logger.info("Claimed job id={}", job.getId());
        return jobRepository.save(job);
    }

    public void execute(Job job) {
        if (isStillRunnable(job)) {
            UUID jobId = job.getId();
            logger.info("Executing job id={}", jobId);

            try {
                workExecutor.execute(job);
                job.setStatus(JobStatus.SUCCESS);
                logger.info("Job id={} completed successfully", jobId);
            } catch (Exception e) {
                logger.error("Job id={} failed due to {}", jobId, e.getMessage());

                int attempts = job.getAttempts() + 1;
                job.setAttempts(attempts);

                if (attempts > job.getMaxAttempts()) {
                    logger.info("Job permanently failed: id= {} attempts={}", jobId, attempts);
                    job.setStatus(JobStatus.FAILED);
                } else {
                    job.setNextRunAt(computeNextRunAt(attempts));
                    logger.info("Retry scheduled: Job id={} attempt={} nextRunAt={}",  jobId,
                            attempts, job.getNextRunAt());
                    job.setStatus(JobStatus.PENDING);
                }
            }

            jobRepository.save(job);
        }
    }

    private boolean isStillRunnable(Job job) {
        var jobOpt = jobRepository.findById(job.getId());
        if (jobOpt.isEmpty()) {
            return false;
        }
        return jobOpt.get().getStatus().equals(JobStatus.RUNNING);
    }

    private Instant computeNextRunAt(int attempts) {
        long seconds = (long) Math.pow(2, attempts);
        return Instant.now().plusSeconds(seconds);
    }
}
