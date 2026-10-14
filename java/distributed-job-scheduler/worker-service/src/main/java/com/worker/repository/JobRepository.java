package com.worker.repository;

import com.worker.model.Job;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface JobRepository extends JpaRepository<Job, UUID> {

    @Query(
            value = """
            SELECT *
            FROM job
            WHERE status = 'PENDING'
              AND next_run_at <= :now
            ORDER BY created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """,
            nativeQuery = true
    )
    Optional<Job> claimNextRunnableJob(@Param("now") Instant now);
}
