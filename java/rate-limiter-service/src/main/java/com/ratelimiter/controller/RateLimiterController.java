package com.ratelimiter.controller;

import com.ratelimiter.dto.RateLimitRequest;
import com.ratelimiter.dto.RateLimitResponse;
import com.ratelimiter.service.RateLimiterService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/check")
public class RateLimiterController {

    private final RateLimiterService rateLimiterService;

    public RateLimiterController(RateLimiterService rateLimiterService) {
        this.rateLimiterService = rateLimiterService;
    }

    @PostMapping
    public RateLimitResponse checkRateLimit(@RequestBody RateLimitRequest request) {
        String apiKey = request.getApiKey();

        if (apiKey == null || apiKey.isBlank()) {
            return new RateLimitResponse(false, 0);
        }

        return rateLimiterService.checkRateLimit(apiKey);
    }
}
