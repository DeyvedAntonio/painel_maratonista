"""Exceções customizadas do domínio."""

from typing import Any


class DomainError(Exception):
    """Base para erros de domínio."""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationError(DomainError):
    """Erro de validação de entrada."""
    def __init__(self, message: str, field: str | None = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class NotFoundError(DomainError):
    """Recurso não encontrado."""
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            f"{resource} não encontrado: {identifier}",
            "NOT_FOUND",
            {"resource": resource, "identifier": identifier},
        )


class ConflictError(DomainError):
    """Conflito de estado (ex: duplicata)."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, "CONFLICT", details)


class UnauthorizedError(DomainError):
    """Acesso não autorizado."""
    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, "UNAUTHORIZED")


class BusinessRuleError(DomainError):
    """Violação de regra de negócio."""
    def __init__(self, message: str, rule: str, details: dict | None = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION", {"rule": rule, **(details or {})})


class ExternalServiceError(DomainError):
    """Erro em serviço externo (TMDb, etc)."""
    def __init__(self, service: str, message: str, original: Exception | None = None):
        super().__init__(
            f"Erro no {service}: {message}",
            "EXTERNAL_SERVICE_ERROR",
            {"service": service, "original": str(original) if original else None},
        )


class DatabaseError(DomainError):
    """Erro de banco de dados."""
    def __init__(self, message: str, operation: str, original: Exception | None = None):
        super().__init__(
            f"Erro no banco ({operation}): {message}",
            "DATABASE_ERROR",
            {"operation": operation, "original": str(original) if original else None},
        )