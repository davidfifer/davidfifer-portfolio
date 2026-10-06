package com.worker.executor;

import com.worker.model.Job;

public interface WorkExecutor {
    void execute(Job job) throws Exception;
}
