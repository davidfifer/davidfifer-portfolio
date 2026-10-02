package com.worker.service;

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
    private static final Logger logger = LoggerFactory.getLogger(WorkerService.class);

    public WorkerService(JobRepository jobRepository) {
        this.jobRepository = jobRepository;
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
        UUID jobId = job.getId();
        logger.info("Executing job id={}", jobId);

        try {
            Thread.sleep(2000);
            job.setStatus(JobStatus.SUCCESS);
            logger.info("Job id={} completed successfully", jobId);
        } catch (Exception e) {
            logger.error("Job id={} failed due to {}", jobId, e.getMessage());
            job.setStatus(JobStatus.FAILED);
        }

        jobRepository.save(job);
    }
}
