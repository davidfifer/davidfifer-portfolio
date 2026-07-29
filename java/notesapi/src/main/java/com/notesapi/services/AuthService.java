package com.notesapi.services;

import com.notesapi.dto.LoginRequestDto;
import com.notesapi.dto.RegisterRequestDto;
import com.notesapi.entities.User;
import com.notesapi.exceptions.DuplicateEmailException;
import com.notesapi.exceptions.InvalidCredentialsException;
import com.notesapi.repositories.UserRepository;
import com.notesapi.security.JwtService;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public AuthService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtService jwtService,
                       AuthenticationManager authenticationManager) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.authenticationManager = authenticationManager;
    }

    // ---------------------------
    // REGISTER
    // ---------------------------
    public String register(RegisterRequestDto request) {

        // Check if email already exists
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new DuplicateEmailException("Email already exists");
        }

        // Create new user
        User user = User.builder()
                .email(request.getEmail())
                .name(request.getName())
                .password(passwordEncoder.encode(request.getPassword()))
                .build();

        userRepository.save(user);

        // Return JWT
        return jwtService.generateToken(user.getEmail());
    }

    // ---------------------------
    // LOGIN
    // ---------------------------
    public String login(LoginRequestDto request) {

        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            request.getEmail(),
                            request.getPassword()
                    )
            );
        } catch (Exception ex) {
            throw new InvalidCredentialsException("Invalid email or password");
        }

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new InvalidCredentialsException("Invalid email or password"));

        return jwtService.generateToken(user.getEmail());
    }
}
