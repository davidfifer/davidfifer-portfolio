package com.notesapi.dto;

import lombok.Data;

@Data
public class RegisterRequestDto {
    private String email;
    private String password;
    private String name;

    public RegisterRequestDto(String email, String password, String name) {
    }
}
