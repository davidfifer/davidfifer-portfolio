package com.ratelimiter.service;

import com.ratelimiter.config.RateLimitProperties;
import com.ratelimiter.dto.RateLimitResponse;
import com.ratelimiter.store.TokenBucketStore;
import org.springframework.stereotype.Service;

@Service
public class RateLimiterService {

    private final RateLimitProperties properties;
    private final TokenBucketStore bucketStore;

    public RateLimiterService(RateLimitProperties properties, TokenBucketStore bucketStore) {
        this.properties = properties;
        this.bucketStore = bucketStore;
    }

    public RateLimitResponse checkRateLimit(String apiKey) {
        return null; // placeholder
    }
}
