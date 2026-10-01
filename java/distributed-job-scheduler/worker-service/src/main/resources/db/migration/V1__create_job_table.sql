CREATE TABLE job (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL,
    attempts INT NOT NULL,
    max_attempts INT NOT NULL,
    next_run_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);
