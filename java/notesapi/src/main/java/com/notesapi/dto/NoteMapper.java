package com.notesapi.dto;

import com.notesapi.entities.Note;

public class NoteMapper {

    public static Note toEntity(NoteRequestDto dto, Long userId) {
        return Note.builder()
                .title(dto.getTitle())
                .content(dto.getContent())
                .userId(userId)
                .build();
    }

    public static NoteResponseDto toResponse(Note note) {
        return NoteResponseDto.builder()
                .id(note.getId())
                .title(note.getTitle())
                .content(note.getContent())
                .createdAt(note.getCreatedAt())
                .updatedAt(note.getUpdatedAt())
                .build();
    }
}
