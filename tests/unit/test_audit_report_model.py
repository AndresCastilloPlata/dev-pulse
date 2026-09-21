import pytest
from pydantic import ValidationError

from src.dev_pulse.domain.entities.audit_report import (AuditReport, AuditStatus, Violation)

def test_crear_audit_report_aprobado_exitoso() -> None:
    """Verifica la instanciacion valida de un reporte con puntaje aprobatorio"""
    reporte = AuditReport(
        commit_sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        status=AuditStatus.APPROVED,
        score=95,
        summary="El commit cumple con PEP 8 y respeta los principios SOLID.",
        violations=[],
        recommendations=["Mantener la cobertura de pruebas sobre el 90%."],
    )

    assert reporte.status == AuditStatus.APPROVED
    assert reporte.score == 95
    assert len(reporte.violations) == 0
    assert len(reporte.recommendations) == 1


def test_crear_audit_report_con_violaciones_rechazado() -> None:
    """Verifica que un reporte con violaciones criticas se registre con REJECTED"""
    violacion = Violation(
        file_path="src/main.py",
        line_number=45,
        rule="SRP (Single Responsibility Principle)",
        description="La clase maneja conexion de red y formateo de datos.",
    )

    reporte = AuditReport(
        commit_sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        status=AuditStatus.REJECTED,
        score=50,
        summary="Se detectaron violaciones de arquitectura.",
        violations=[violacion],
        recommendations=["Separar el formateo en una clase auxiliar."],
    )

    assert reporte.status == AuditStatus.REJECTED
    assert reporte.score == 50
    assert len(reporte.violations) == 1
    assert reporte.violations[0].rule == "SRP (Single Responsibility Principle)"


def test_audit_report_falla_con_score_fuera_de_rango() -> None:
    """Verifica que el modelo rechace lecturas anomalas fuera de 0 y 100"""
    with pytest.raises(ValidationError):
        AuditReport(
            commit_sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
            status=AuditStatus.APPROVED,
            score=105,  # Fuera de rango (sobretension)
            summary="Reporte invalido por score excesivo.",
            violations=[],
            recommendations=[],
        )


def test_audit_report_falla_si_aprobado_con_score_menor_a_70() -> None:
    """Invariante de negocio: Un puntaje menor a 70 nunca puede estar APROBADO"""
    with pytest.raises(ValidationError):
        AuditReport(
            commit_sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
            status=AuditStatus.APPROVED,
            score=65,  # Incoherencia logica
            summary="Reporte incoherente.",
            violations=[],
            recommendations=[],
        )