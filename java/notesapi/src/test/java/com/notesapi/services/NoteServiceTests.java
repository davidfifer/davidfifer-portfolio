package com.notesapi.services;

import com.notesapi.dto.NoteRequestDto;
import com.notesapi.dto.NoteResponseDto;
import com.notesapi.entities.Note;
import com.notesapi.exceptions.NotFoundException;
import com.notesapi.repositories.NoteRepository;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class NoteServiceTests {

    @Mock
    private NoteRepository noteRepository;

    @InjectMocks
    private NoteServiceImpl noteService;

    public NoteServiceTests() {
        MockitoAnnotations.openMocks(this);
    }

    // -----------------------------------------------------
    // CREATE
    // -----------------------------------------------------

    @Test
    void create_ShouldCreateNote() {
        Long userId = 10L;

        NoteRequestDto dto = new NoteRequestDto();
        dto.setTitle("Test Title");
        dto.setContent("Test Content");

        Note saved = new Note();
        saved.setId(1L);
        saved.setUserId(userId);
        saved.setTitle("Test Title");
        saved.setContent("Test Content");
        saved.setCreatedAt(Instant.now());
        saved.setUpdatedAt(Instant.now());

        when(noteRepository.save(any(Note.class))).thenReturn(saved);

        NoteResponseDto result = noteService.create(dto, userId);

        assertEquals("Test Title", result.getTitle());
        assertEquals("Test Content", result.getContent());
        assertEquals(saved.getId(), result.getId());
        assertEquals(saved.getCreatedAt(), result.getCreatedAt());
        assertEquals(saved.getUpdatedAt(), result.getUpdatedAt());
    }

    // -----------------------------------------------------
    // GET ALL
    // -----------------------------------------------------

    @Test
    void getAll_ShouldReturnPagedNotes() {
        Long userId = 10L;

        Note note = new Note();
        note.setId(1L);
        note.setUserId(userId);
        note.setTitle("Title");
        note.setContent("Content");
        note.setCreatedAt(Instant.now());
        note.setUpdatedAt(Instant.now());

        Page<Note> page = new PageImpl<>(List.of(note));

        when(noteRepository.findByUserId(eq(userId), any(Pageable.class)))
                .thenReturn(page);

        Page<NoteResponseDto> result = noteService.getAll(userId, 0, 10);

        assertEquals(1, result.getTotalElements());
        assertEquals("Title", result.getContent().get(0).getTitle());
    }

    // -----------------------------------------------------
    // GET BY ID
    // -----------------------------------------------------

    @Test
    void getById_ShouldReturnNote() {
        Long noteId = 1L;
        Long userId = 10L;

        Note existing = new Note();
        existing.setId(noteId);
        existing.setUserId(userId);
        existing.setTitle("Title");
        existing.setContent("Content");
        existing.setCreatedAt(Instant.now());
        existing.setUpdatedAt(Instant.now());

        when(noteRepository.findByIdAndUserId(noteId, userId))
                .thenReturn(Optional.of(existing));

        NoteResponseDto result = noteService.getById(noteId, userId);

        assertEquals("Title", result.getTitle());
        assertEquals("Content", result.getContent());
        assertEquals(noteId, result.getId());
    }

    @Test
    void getById_ShouldThrow_WhenNoteNotFound() {
        when(noteRepository.findByIdAndUserId(anyLong(), anyLong()))
                .thenReturn(Optional.empty());

        assertThrows(NotFoundException.class,
                () -> noteService.getById(1L, 10L));
    }

    // -----------------------------------------------------
    // UPDATE
    // -----------------------------------------------------

    @Test
    void update_ShouldUpdateNote() {
        Long noteId = 1L;
        Long userId = 10L;

        Note existing = new Note();
        existing.setId(noteId);
        existing.setUserId(userId);
        existing.setTitle("Old Title");
        existing.setContent("Old Content");
        existing.setCreatedAt(Instant.now());
        existing.setUpdatedAt(Instant.now());

        NoteRequestDto dto = new NoteRequestDto();
        dto.setTitle("New Title");
        dto.setContent("New Content");

        Note saved = new Note();
        saved.setId(noteId);
        saved.setUserId(userId);
        saved.setTitle("New Title");
        saved.setContent("New Content");
        saved.setCreatedAt(existing.getCreatedAt());
        saved.setUpdatedAt(Instant.now());

        when(noteRepository.findByIdAndUserId(noteId, userId))
                .thenReturn(Optional.of(existing));

        when(noteRepository.save(any(Note.class))).thenReturn(saved);

        NoteResponseDto result = noteService.update(noteId, dto, userId);

        assertEquals("New Title", result.getTitle());
        assertEquals("New Content", result.getContent());
        assertEquals(noteId, result.getId());
        assertEquals(saved.getCreatedAt(), result.getCreatedAt());
        assertEquals(saved.getUpdatedAt(), result.getUpdatedAt());
    }

    @Test
    void update_ShouldThrow_WhenNoteNotFound() {
        when(noteRepository.findByIdAndUserId(anyLong(), anyLong()))
                .thenReturn(Optional.empty());

        NoteRequestDto dto = new NoteRequestDto();
        dto.setTitle("New Title");
        dto.setContent("New Content");

        assertThrows(NotFoundException.class,
                () -> noteService.update(1L, dto, 10L));
    }

    // -----------------------------------------------------
    // DELETE
    // -----------------------------------------------------

    @Test
    void delete_ShouldDeleteNote() {
        Long noteId = 1L;
        Long userId = 10L;

        Note existing = new Note();
        existing.setId(noteId);
        existing.setUserId(userId);

        when(noteRepository.findByIdAndUserId(noteId, userId))
                .thenReturn(Optional.of(existing));

        doNothing().when(noteRepository).delete(existing);

        noteService.delete(noteId, userId);

        verify(noteRepository).delete(existing);
    }

    @Test
    void delete_ShouldThrow_WhenNoteNotFound() {
        when(noteRepository.findByIdAndUserId(anyLong(), anyLong()))
                .thenReturn(Optional.empty());

        assertThrows(NotFoundException.class,
                () -> noteService.delete(1L, 10L));
    }
}
