package com.notesapi.services;

import com.notesapi.dto.NoteRequestDto;
import com.notesapi.dto.NoteResponseDto;
import org.springframework.data.domain.Page;

public interface NoteService {

    NoteResponseDto create(NoteRequestDto dto, Long userId);

    Page<NoteResponseDto> getAll(Long userId, int page, int size);

    NoteResponseDto getById(Long id, Long userId);

    NoteResponseDto update(Long id, NoteRequestDto dto, Long userId);

    void delete(Long id, Long userId);
}
