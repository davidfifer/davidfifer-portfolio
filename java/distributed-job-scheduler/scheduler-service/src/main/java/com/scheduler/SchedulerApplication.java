package com.scheduler;

import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SchedulerApplication {

    private static final Logger logger = LoggerFactory.getLogger(SchedulerApplication.class);

    public static void main(String[] args) {
        SpringApplication.run(SchedulerApplication.class, args);
    }

    @PostConstruct
    public void onStart() {
        logger.info("Scheduler service started successfully");
    }
}
