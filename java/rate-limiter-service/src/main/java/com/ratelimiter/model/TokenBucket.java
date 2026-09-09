package com.ratelimiter.model;

public class TokenBucket {

    private double tokens;
    private final int capacity;
    private final int refillRate;
    private long lastRefillTimestamp;

    public TokenBucket(int capacity, int refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefillTimestamp = System.currentTimeMillis();
    }

    public synchronized boolean tryConsume() {
        refill();

        if (tokens >= 1.0) {
            tokens -= 1.0;
            return true;
        }

        return false;
    }

    private void refill() {
        long currentTime = System.currentTimeMillis();
        long elapsedMs = currentTime - lastRefillTimestamp;

        if (elapsedMs <= 0) {
            return;
        }

        double elapsedSeconds = elapsedMs / 1000.0;
        double tokensToAdd = elapsedSeconds * refillRate;

        tokens = Math.min(capacity, tokens + tokensToAdd);
        lastRefillTimestamp = currentTime;
    }

    public double getTokens() {
        return tokens;
    }

}
