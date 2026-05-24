"""
Unit and integration tests for the FastAPI automation REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from reacton.api.server import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"

def test_api_simulate():
    payload = {
        "aluminum_mass_kg": 0.5,
        "water_mass_kg": 2.0,
        "d_ox_nm": 3.0,
        "particle_size_mean_um": 25.0,
        "particle_size_std_um": 5.0,
        "pH": 12.5,
        "water_type": "tap",
        "catalyst_molar": 0.1,
        "reactor_volume_l": 5.0,
        "cooling_duty_w": 200.0,
        "initial_temp_c": 25.0,
        "initial_pressure_bar": 1.0,
        "dt": 1.0,
        "max_time_s": 5.0
    }
    res = client.post("/api/v1/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "summary" in data
    assert "telemetry" in data
    assert len(data["telemetry"]) > 0

def test_api_optimize():
    payload = {
        "objective": "maximize_h2_rate",
        "feedstock_type": "premium",
        "water_type": "tap",
        "target_purity": 0.99,
        "max_pressure_bar": 10.0,
        "max_temp_c": 95.0
    }
    res = client.post("/api/v1/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "optimal_parameters" in data
    assert "metrics" in data

def test_api_asme_compliance():
    payload = {
        "design_pressure_bar": 12.0,
        "reactor_radius_mm": 120.0,
        "allowable_stress_mpa": 138.0,
        "joint_efficiency": 0.85,
        "corrosion_allowance_mm": 1.5
    }
    res = client.post("/api/v1/compliance/asme", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["calculated_shell_thickness_mm"] > 1.5
    assert data["calculated_head_thickness_mm"] > 1.5
