package com.abhayraj.founderbrain.Security;

import com.abhayraj.founderbrain.model.User;
import com.abhayraj.founderbrain.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import java.util.List;
import java.io.IOException;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private final JwtService jwtService;
    private final UserRepository userRepository;

    @Override
    protected void doFilterInternal(

            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain)
            throws ServletException, IOException {
           System.out.println("==== FILTER DEBUG START ====");
        if (request.getServletPath().startsWith("/auth")) {
            System.out.println("Auth endpoint, skipping filter");
            filterChain.doFilter(request, response);
            return;
        }

        final String authHeader = request.getHeader("Authorization");
        System.out.println("HEADER: " + authHeader);
        final String token;
        final String username;

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            System.out.println("No JWT token found");
            filterChain.doFilter(request, response);
            return;
        }

        token = authHeader.substring(7);
        System.out.println("TOKEN: " + token);
        username = jwtService.extractUser(token);
        System.out.println("USERNAME: " + username);

        if (username != null &&
                SecurityContextHolder.getContext().getAuthentication() == null) {

            User user = userRepository.findByEmail(username)
                    .orElseThrow(() -> new RuntimeException("User not found"));
            System.out.println("USER: " + user);
            System.out.println("ROLE: " + (user != null ? user.getRole() : "null"));

            if (jwtService.isTokenValid(token, user.getEmail())) {

                String role = user.getRole() != null ? user.getRole() : "USER";

                SimpleGrantedAuthority authority =
                        new SimpleGrantedAuthority("ROLE_" + role);


                UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                                user,
                                null,
                                List.of(authority)
                        );


                authToken.setDetails(
                        new WebAuthenticationDetailsSource()
                                .buildDetails(request)
                );

                SecurityContextHolder.getContext()
                        .setAuthentication(authToken);

                System.out.println("✅ Authentication set successfully");
            }
        }
        System.out.println("==== FILTER DEBUG END ====");
        filterChain.doFilter(request, response);
    }

}

