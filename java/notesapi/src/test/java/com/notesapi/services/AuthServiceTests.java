package com.notesapi.services;

import com.notesapi.dto.LoginRequestDto;
import com.notesapi.dto.RegisterRequestDto;
import com.notesapi.entities.User;
import com.notesapi.exceptions.DuplicateEmailException;
import com.notesapi.exceptions.InvalidCredentialsException;
import com.notesapi.repositories.UserRepository;
import com.notesapi.security.JwtService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockitoAnnotations;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class AuthServiceTests {

    private UserRepository userRepository;
    private PasswordEncoder passwordEncoder;
    private JwtService jwtService;
    private AuthenticationManager authenticationManager;

    private AuthService authService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);

        userRepository = mock(UserRepository.class);
        passwordEncoder = mock(PasswordEncoder.class);
        jwtService = mock(JwtService.class);
        authenticationManager = mock(AuthenticationManager.class);

        authService = new AuthService(
                userRepository,
                passwordEncoder,
                jwtService,
                authenticationManager
        );
    }

    // ------------------------------------------------------------
    // 1. REGISTER FLOW
    // ------------------------------------------------------------
    @Test
    void register_ShouldCreateUserAndReturnToken() {
        RegisterRequestDto request = new RegisterRequestDto(
                "test@example.com",
                "password123",
                "test"
        );

        when(userRepository.findByEmail(request.getEmail()))
                .thenReturn(Optional.empty());

        when(passwordEncoder.encode(request.getPassword()))
                .thenReturn("hashed-password");

        when(jwtService.generateToken(request.getEmail()))
                .thenReturn("mock.jwt.token");

        String token = authService.register(request);

        assertEquals("mock.jwt.token", token);

        verify(userRepository, times(1)).findByEmail(request.getEmail());
        verify(passwordEncoder, times(1)).encode(request.getPassword());
        verify(userRepository, times(1)).save(any(User.class));
        verify(jwtService, times(1)).generateToken(request.getEmail());
    }

    @Test
    void register_ShouldThrowDuplicateEmailException() {
        RegisterRequestDto request = new RegisterRequestDto(
                "test@example.com",
                "password123",
                "test"
        );

        when(userRepository.findByEmail(request.getEmail()))
                .thenReturn(Optional.of(new User()));

        assertThrows(DuplicateEmailException.class,
                () -> authService.register(request));

        verify(userRepository, times(1)).findByEmail(request.getEmail());
        verify(userRepository, never()).save(any());
        verify(jwtService, never()).generateToken(any());
    }

    // ------------------------------------------------------------
    // 2. LOGIN FLOW
    // ------------------------------------------------------------
    @Test
    void login_ShouldAuthenticateAndReturnToken() {
        LoginRequestDto request = new LoginRequestDto(
                "test@example.com",
                "password123"
        );

        Authentication mockAuth = mock(Authentication.class);

        when(authenticationManager.authenticate(
                argThat(auth ->
                        auth instanceof UsernamePasswordAuthenticationToken &&
                                auth.getName().equals(request.getEmail())
                )
        )).thenReturn(mockAuth);

        User user = User.builder()
                .email(request.getEmail())
                .password("hashed-password")
                .build();

        when(userRepository.findByEmail(request.getEmail()))
                .thenReturn(Optional.of(user));

        when(jwtService.generateToken(request.getEmail()))
                .thenReturn("mock.jwt.token");

        String token = authService.login(request);

        assertEquals("mock.jwt.token", token);

        verify(authenticationManager, times(1)).authenticate(any());
        verify(userRepository, times(1)).findByEmail(request.getEmail());
        verify(jwtService, times(1)).generateToken(request.getEmail());
    }

    @Test
    void login_ShouldThrowInvalidCredentialsException_WhenAuthFails() {
        LoginRequestDto request = new LoginRequestDto(
                "test@example.com",
                "password123"
        );

        doThrow(new RuntimeException("Auth failed"))
                .when(authenticationManager).authenticate(any());

        assertThrows(InvalidCredentialsException.class,
                () -> authService.login(request));

        verify(authenticationManager, times(1)).authenticate(any());
        verify(userRepository, never()).findByEmail(any());
        verify(jwtService, never()).generateToken(any());
    }

    @Test
    void login_ShouldThrowInvalidCredentialsException_WhenUserNotFound() {
        LoginRequestDto request = new LoginRequestDto(
                "missing@example.com",
                "password123"
        );

        when(authenticationManager.authenticate(
                argThat(auth ->
                        auth instanceof UsernamePasswordAuthenticationToken &&
                                auth.getName().equals(request.getEmail())
                )
        )).thenReturn(mock(Authentication.class));

        when(userRepository.findByEmail(request.getEmail()))
                .thenReturn(Optional.empty());

        assertThrows(InvalidCredentialsException.class,
                () -> authService.login(request));

        verify(authenticationManager, times(1)).authenticate(any());
        verify(userRepository, times(1)).findByEmail(request.getEmail());
        verify(jwtService, never()).generateToken(any());
    }

    // ------------------------------------------------------------
    // 3. TOKEN GENERATION (simple unit test)
    // ------------------------------------------------------------
    @Test
    void generateToken_ShouldReturnValidToken() {
        String email = "test@example.com";

        when(jwtService.generateToken(email))
                .thenReturn("mock.jwt.token");

        String token = jwtService.generateToken(email);

        assertEquals("mock.jwt.token", token);

        verify(jwtService, times(1)).generateToken(email);
    }
}
