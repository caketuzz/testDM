-- ============================================================
-- Migration 001 - Initial schema
-- ============================================================

-- Email case-insensitive support
CREATE EXTENSION IF NOT EXISTS citext;

-- ============================================================
-- Users
-- ============================================================

CREATE TABLE users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email CITEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'ACTIVE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at TIMESTAMPTZ
);

-- ============================================================
-- Activation codes
-- ============================================================

CREATE TABLE activation_codes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,
    code_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_activation_codes_user UNIQUE (user_id)
);



