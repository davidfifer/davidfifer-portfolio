package com.notesapi.controllers;

import com.notesapi.dto.NoteRequestDto;
import com.notesapi.dto.NoteResponseDto;
import com.notesapi.services.NoteService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/notes")
@RequiredArgsConstructor
public class NoteController {

    private final NoteService noteService;

    @PostMapping
    public ResponseEntity<NoteResponseDto> createNote(
            @Valid @RequestBody NoteRequestDto dto,
            @RequestHeader("X-User-Id") Long userId
    ) {
        NoteResponseDto created = noteService.create(dto, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public Page<NoteResponseDto> getAllNotes(
            @RequestHeader("X-User-Id") Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return noteService.getAll(userId, page, size);
    }

    @GetMapping("/{id}")
    public NoteResponseDto getNoteById(
            @PathVariable Long id,
            @RequestHeader("X-User-Id") Long userId
    ) {
        return noteService.getById(id, userId);
    }

    @PutMapping("/{id}")
    public NoteResponseDto updateNote(
            @PathVariable Long id,
            @Valid @RequestBody NoteRequestDto dto,
            @RequestHeader("X-User-Id") Long userId
    ) {
        return noteService.update(id, dto, userId);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteNote(
            @PathVariable Long id,
            @RequestHeader("X-User-Id") Long userId
    ) {
        noteService.delete(id, userId);
        return ResponseEntity.noContent().build();
    }
}
