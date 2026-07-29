package com.notesapi.entities;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;      // user's email (unique identifier)

    @Column(nullable = false)
    private String name;       // user's display name

    @Column(nullable = false)
    private String password;   // hashed password
}
