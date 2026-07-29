package com.notesapi.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class NoteRequestDto {

    @NotBlank(message = "Title cannot be empty")
    @Size(max = 255, message = "Title cannot exceed 255 characters")
    private String title;

    @NotBlank(message = "Content cannot be empty")
    @Size(max = 5000, message = "Content cannot exceed 5000 characters")
    private String content;

    public NoteRequestDto() {
    }
}
