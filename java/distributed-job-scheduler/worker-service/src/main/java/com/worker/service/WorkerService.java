package com.worker.service;

import com.worker.executor.WorkExecutor;
import com.worker.metrics.JobMetrics;
import com.worker.model.Job;
import com.worker.model.JobStatus;
import com.worker.repository.JobRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

@Service
public class WorkerService {

    @Value("${WORKER_ID:unknown}")
    private String workerId = "unknown";

    private final JobMetrics jobMetrics;
    private final JobRepository jobRepository;
    private final WorkExecutor workExecutor;

    private static final Logger logger = LoggerFactory.getLogger(WorkerService.class);

    public WorkerService(JobRepository jobRepository, WorkExecutor workExecutor, JobMetrics jobMetrics) {
        this.jobRepository = jobRepository;
        this.workExecutor = workExecutor;
        this.jobMetrics = jobMetrics;
    }

    @Transactional
    public Optional<Job> claimNextJob() {
        var jobOpt = jobRepository.claimNextRunnableJob(Instant.now());

        if (jobOpt.isEmpty()) {
            return Optional.empty();
        }

        Job job = jobOpt.get();
        job.setStatus(JobStatus.RUNNING);

        logger.info("[{}] Claimed job id={}", workerId, job.getId());
        return Optional.of(jobRepository.save(job));
    }

    public void execute(Job job) {
        if (isStillRunnable(job)) {
            UUID jobId = job.getId();
            logger.info("[{}] Executing job id={}", workerId, jobId);

            try {
                workExecutor.execute(job);
                jobMetrics.recordSuccess();
                job.setStatus(JobStatus.SUCCESS);
                logger.info("[{}] Job id={} completed successfully", workerId, jobId);
            } catch (Exception e) {
                jobMetrics.recordFailure();

                logger.error("[{}] Job id={} failed due to {}", workerId, jobId, e.getMessage());

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
