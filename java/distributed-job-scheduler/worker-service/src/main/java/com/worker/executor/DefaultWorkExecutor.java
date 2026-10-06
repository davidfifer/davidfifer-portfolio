package com.worker.executor;

import com.worker.model.Job;
import org.springframework.stereotype.Service;

@Service
public class DefaultWorkExecutor implements WorkExecutor {
    @Override
    public void execute(Job job) throws Exception {
        Thread.sleep(2000);
    }
}
