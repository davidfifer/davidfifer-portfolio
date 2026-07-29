package com.notesapi.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data
@Builder
public class NoteResponseDto {
    private Long id;
    private String title;
    private String content;
    private Instant createdAt;
    private Instant updatedAt;
}
