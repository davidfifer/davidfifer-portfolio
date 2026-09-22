package com.ratelimiter.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class TokenBucketTest {

    @Test
    void consumeSucceedsWhenTokensAvailable() {
        TokenBucket bucket = new TokenBucket(10, 5);
        assertTrue(bucket.tryConsume());
        assertEquals(9, bucket.getTokens(), 0.01);
    }

    @Test
    void consumeFailsWhenEmpty() {
        TokenBucket bucket = new TokenBucket(1, 1);
        bucket.tryConsume(); // now empty
        assertFalse(bucket.tryConsume());
    }

    @Test
    void refillCapsAtCapacityBeforeConsumption() throws InterruptedException {
        TokenBucket bucket = new TokenBucket(5, 100); // refills very fast
        bucket.tryConsume(); // 4 left

        Thread.sleep(50); // allow refill

        bucket.tryConsume(); // triggers refill
        assertEquals(4, bucket.getTokens(), 0.01); // refill capped at capacity
    }

    @Test
    void refillAddsCorrectAmountBasedOnTime() throws InterruptedException {
        TokenBucket bucket = new TokenBucket(10, 2); // 2 tokens/sec
        bucket.tryConsume(); // 9 left

        Thread.sleep(500); // half a second → +1 token

        bucket.tryConsume(); // triggers refill
        assertEquals(9, bucket.getTokens(), 0.01);
    }

    @Test
    void refillOnlyOccursOnTryConsume() throws InterruptedException {
        TokenBucket bucket = new TokenBucket(10, 10);
        bucket.tryConsume(); // 9 left

        Thread.sleep(500); // should add 5 tokens, but not yet applied

        assertEquals(9, bucket.getTokens(), 0.01); // no refill until tryConsume()

        bucket.tryConsume(); // triggers refill
        assertEquals(9, bucket.getTokens(), 0.01); // refill to 10, then consume to 9
    }

    @Test
    void zeroRefillRateNeverAddsTokens() throws InterruptedException {
        TokenBucket bucket = new TokenBucket(5, 0);
        bucket.tryConsume(); // 4 left

        Thread.sleep(1000); // no refill should occur

        bucket.tryConsume(); // still no refill
        assertEquals(3, bucket.getTokens(), 0.01);
    }

    @Test
    void noRefillWhenElapsedTimeIsZero() {
        TokenBucket bucket = new TokenBucket(5, 100);
        bucket.tryConsume(); // 4 left

        // Immediately consume again — elapsedMs <= 0
        bucket.tryConsume(); // should NOT refill
        assertEquals(3, bucket.getTokens(), 0.01);
    }
}
