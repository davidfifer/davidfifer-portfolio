package com.notesapi.services;

import com.notesapi.dto.NoteRequestDto;
import com.notesapi.dto.NoteResponseDto;
import com.notesapi.entities.Note;
import com.notesapi.exceptions.NotFoundException;
import com.notesapi.repositories.NoteRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
@RequiredArgsConstructor
public class NoteServiceImpl implements NoteService {

    private final NoteRepository noteRepository;

    @Override
    public NoteResponseDto create(NoteRequestDto dto, Long userId) {
        Note note = Note.builder()
                .title(dto.getTitle())
                .content(dto.getContent())
                .createdAt(Instant.now())
                .updatedAt(Instant.now())
                .userId(userId)
                .build();

        return toResponse(noteRepository.save(note));
    }

    @Override
    public Page<NoteResponseDto> getAll(Long userId, int page, int size) {
        Page<Note> notes = noteRepository.findByUserId(userId, PageRequest.of(page, size));
        return notes.map(this::toResponse);
    }

    @Override
    public NoteResponseDto getById(Long id, Long userId) {
        Note note = noteRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new NotFoundException("Note not found"));
        return toResponse(note);
    }

    @Override
    public NoteResponseDto update(Long id, NoteRequestDto dto, Long userId) {
        Note existing = noteRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new NotFoundException("Note not found"));

        existing.setTitle(dto.getTitle());
        existing.setContent(dto.getContent());
        existing.setUpdatedAt(Instant.now());

        return toResponse(noteRepository.save(existing));
    }

    @Override
    public void delete(Long id, Long userId) {
        Note existing = noteRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new NotFoundException("Note not found"));
        noteRepository.delete(existing);
    }

    private NoteResponseDto toResponse(Note note) {
        return NoteResponseDto.builder()
                .id(note.getId())
                .title(note.getTitle())
                .content(note.getContent())
                .createdAt(note.getCreatedAt())
                .updatedAt(note.getUpdatedAt())
                .build();
    }
}
