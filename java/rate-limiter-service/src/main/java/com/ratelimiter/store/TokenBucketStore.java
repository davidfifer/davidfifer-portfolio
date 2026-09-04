package com.ratelimiter.store;

import com.ratelimiter.model.TokenBucket;
import java.util.concurrent.ConcurrentHashMap;

public class TokenBucketStore {

    private final ConcurrentHashMap<String, TokenBucket> buckets = new ConcurrentHashMap<>();

    public TokenBucket getOrCreateBucket(String apiKey, int capacity, int refillRate) {
        return buckets.computeIfAbsent(apiKey, key -> new TokenBucket(capacity, refillRate));
    }
}
