package com.ratelimiter.store;

import com.ratelimiter.config.RateLimitProperties;
import com.ratelimiter.model.TokenBucket;
import java.util.concurrent.ConcurrentHashMap;

public class TokenBucketStore {

    private final RateLimitProperties properties;
    private final ConcurrentHashMap<String, TokenBucket> buckets = new ConcurrentHashMap<>();

    public TokenBucketStore(RateLimitProperties properties) {
        this.properties = properties;
    }

    public TokenBucket getOrCreateBucket(String apiKey) {
        return buckets.computeIfAbsent(apiKey, key -> {
            RateLimitProperties.Limit limit = properties.getLimitFor(apiKey);
            return new TokenBucket(limit.getCapacity(), limit.getRefillRate());
        });
    }
}
