package com.ratelimiter.model;

public class TokenBucket {

    private final int capacity;
    private final int refillRate;
    private double tokens;
    private long lastRefillTimestamp;

    public TokenBucket(int capacity, int refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefillTimestamp = System.nanoTime();
    }

    public synchronized boolean tryConsume() {
        return false; // placeholder
    }

    private void refill() {
        // placeholder
    }
}
