package com.scheduler.controller;

import com.scheduler.dto.JobStatusResponse;
import com.scheduler.dto.SubmitJobRequest;
import com.scheduler.dto.SubmitJobResponse;
import com.scheduler.service.JobService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/jobs")
public class JobController {

    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    @PostMapping("/submit")
    public SubmitJobResponse submitJob(@Valid @RequestBody SubmitJobRequest request) {
        return jobService.submitJob(request);
    }

    @GetMapping("/{id}")
    public JobStatusResponse getStatus(@PathVariable UUID id) {
        return jobService.getStatus(id);
    }
}
