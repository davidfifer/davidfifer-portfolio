package com.ratelimiter.store;

import com.ratelimiter.config.RateLimitProperties;
import com.ratelimiter.model.TokenBucket;
import java.util.concurrent.ConcurrentHashMap;

public class TokenBucketStore {
    private int capacity;
    private int refillRate;

    private final ConcurrentHashMap<String, TokenBucket> buckets = new ConcurrentHashMap<>();

    public TokenBucketStore(RateLimitProperties properties) {
        this.capacity = properties.getDefaultLimit().getCapacity();
        this.refillRate = properties.getDefaultLimit().getRefillRate();
    }

    public TokenBucket getOrCreateBucket(String apiKey) {
        return buckets.computeIfAbsent(apiKey, key -> new TokenBucket(capacity, refillRate));
    }
}
