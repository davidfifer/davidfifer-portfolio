package com.ratelimiter.service;

import com.ratelimiter.config.RateLimitProperties;
import com.ratelimiter.dto.RateLimitResponse;
import com.ratelimiter.store.TokenBucketStore;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class RateLimiterServiceTest {

    private RateLimiterService service;
    private RateLimitProperties props;

    @BeforeEach
    void setup() {
        props = new RateLimitProperties();

        // default bucket
        RateLimitProperties.Limit defaultLimit = new RateLimitProperties.Limit();
        defaultLimit.setCapacity(10);
        defaultLimit.setRefillRate(5);
        props.setDefaultLimit(defaultLimit);

        // custom bucket
        RateLimitProperties.Limit userLimit = new RateLimitProperties.Limit();
        userLimit.setCapacity(20);
        userLimit.setRefillRate(10);
        props.setApiKeys(Map.of("user123", userLimit));

        TokenBucketStore store = new TokenBucketStore(props);
        service = new RateLimiterService(props, store);
    }

    @Test
    void defaultBucketUsedForUnknownKey() {
        RateLimitResponse response = service.checkRateLimit("unknown");
        assertTrue(response.isAllowed());
        assertEquals(9, response.getRemainingTokens());
    }

    @Test
    void customBucketUsedForKnownKey() {
        RateLimitResponse response = service.checkRateLimit("user123");
        assertTrue(response.isAllowed());
        assertEquals(19, response.getRemainingTokens());
    }

    @Test
    void bucketIsReusedAcrossCalls() {
        service.checkRateLimit("user123"); // consume 1
        RateLimitResponse response = service.checkRateLimit("user123"); // consume 1 more

        assertEquals(18, response.getRemainingTokens());
    }

    @Test
    void denialWhenBucketEmpty() {
        // default bucket capacity = 10
        for (int i = 0; i < 10; i++) {
            assertTrue(service.checkRateLimit("unknown").isAllowed());
        }

        RateLimitResponse denied = service.checkRateLimit("unknown");
        assertFalse(denied.isAllowed());
    }

    @Test
    void refillOccursOverTime() throws InterruptedException {
        RateLimitResponse first = service.checkRateLimit("user123"); // 19 left
        assertEquals(19, first.getRemainingTokens());

        Thread.sleep(500); // half a second → +5 tokens (refillRate=10/sec)

        RateLimitResponse second = service.checkRateLimit("user123");
        // refill to 20, then consume 1 → 19
        assertEquals(19, second.getRemainingTokens());
    }

    @Test
    void multipleApiKeysAreIndependent() {
        RateLimitResponse r1 = service.checkRateLimit("user123"); // 19 left
        RateLimitResponse r2 = service.checkRateLimit("unknown"); // 9 left

        assertEquals(19, r1.getRemainingTokens());
        assertEquals(9, r2.getRemainingTokens());
    }
}
