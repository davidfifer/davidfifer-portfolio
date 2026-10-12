package com.worker.metrics;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Component;

@Component
public class JobMetrics {

    private final Counter successCounter;
    private final Counter failureCounter;

    public JobMetrics(MeterRegistry registry) {
        this.successCounter = Counter.builder("jobs.executed.success")
                .description("Number of successfully executed jobs")
                .register(registry);

        this.failureCounter = Counter.builder("jobs.executed.failure")
                .description("Number of failed jobs")
                .register(registry);
    }

    public void recordSuccess() {
        successCounter.increment();
    }

    public void recordFailure() {
        failureCounter.increment();
    }
}
