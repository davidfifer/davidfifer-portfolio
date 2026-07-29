package com.notesapi.repositories;

import com.notesapi.entities.Note;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.Optional;

public interface NoteRepository extends JpaRepository<Note, Long> {

    Page<Note> findByUserId(Long userId, Pageable pageable);

    Optional<Note> findByIdAndUserId(Long id, Long userId);
}
