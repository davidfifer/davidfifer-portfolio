package com.ratelimiter.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
@ConfigurationProperties(prefix = "rate-limits")
public class RateLimitProperties {

    private Limit defaultLimit;
    private Map<String, Limit> apiKeys;

    public static class Limit {
        private int capacity;
        private int refillRate;
        // getters/setters
    }
}
