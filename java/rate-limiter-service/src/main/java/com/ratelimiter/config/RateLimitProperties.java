package com.ratelimiter.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
@ConfigurationProperties(prefix = "rate-limits")
public class RateLimitProperties {

    private Limit defaultLimit;
    private Map<String, Limit> apiKeys;

    public Limit getDefaultLimit() {
        return defaultLimit;
    }

    public void setDefaultLimit(Limit defaultLimit) {
        this.defaultLimit = defaultLimit;
    }

    public Map<String, Limit> getApiKeys() {
        return apiKeys;
    }

    public void setApiKeys(Map<String, Limit> apiKeys) {
        this.apiKeys = apiKeys;
    }

    public Limit getLimitFor(String apiKey) {
        if (apiKeys != null && apiKeys.containsKey(apiKey)) {
            return apiKeys.get(apiKey);
        }
        return defaultLimit;
    }

    public static class Limit {
        private int capacity;
        private int refillRate;

        public int getCapacity() {
            return capacity;
        }

        public void setCapacity(int capacity) {
            this.capacity = capacity;
        }

        public int getRefillRate() {
            return refillRate;
        }

        public void setRefillRate(int refillRate) {
            this.refillRate = refillRate;
        }
    }
}
