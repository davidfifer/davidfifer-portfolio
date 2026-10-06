package com.worker.repository;

import com.worker.model.Job;
import com.worker.model.JobStatus;
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
            SELECT * FROM job
            WHERE status = :status
              AND next_run_at <= :now
            ORDER BY created_at ASC
            LIMIT 1
        """,
        nativeQuery = true
    )
    Optional<Job> findNextRunnableJob(
            @Param("status") JobStatus status,
            @Param("now") Instant now
    );
}
