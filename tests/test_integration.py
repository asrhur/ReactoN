"""
Unit and integration tests for control interfaces, industrial systems, and compliance.
"""

import pytest
from reacton.integration.industrial_systems import PEMFuelCellModel, CoolingLoopModel
from reacton.integration.control_interface import PIDController, VirtualPLC
from reacton.integration.data_acquisition import TelemetryGenerator, SignalFilter
from reacton.compliance.safety_analyzer import AWRSafetyAnalyzer
from reacton.compliance.regulatory_calcs import ASMEPressureVesselCalc, ISO16110Compliance

def test_pem_fuel_cell():
    fc = PEMFuelCellModel(num_cells=10)
    # Open circuit checks
    losses_oc = fc.calculate_cell_losses(current_density_a_cm2=0.0, temp_c=80.0)
    assert losses_oc["voltage_v"] == 1.15
    
    # Active stack loading
    stack = fc.simulate_stack(current_amps=15.0, temp_c=75.0)
    assert stack["stack_voltage_v"] < 11.5
    assert stack["power_output_w"] > 0.0
    assert stack["h2_consumption_g_s"] > 0.0

def test_cooling_loop():
    hx = CoolingLoopModel(overall_u_w_m2k=800.0, area_m2=0.1)
    # Reactor hotter than coolant -> heat should dissipate
    q_cool = hx.calculate_heat_dissipation(reactor_temp_c=80.0, coolant_inlet_temp_c=20.0, coolant_flow_rate_l_min=2.0)
    assert q_cool > 0.0
    
    # No flow -> no dissipation
    q_no_flow = hx.calculate_heat_dissipation(reactor_temp_c=80.0, coolant_inlet_temp_c=20.0, coolant_flow_rate_l_min=0.0)
    assert q_no_flow == 0.0

def test_pid_controller():
    pid = PIDController(Kp=1.0, Ki=0.5, Kd=0.1, setpoint=50.0, output_min=0.0, output_max=10.0)
    # Error is positive (setpoint 50 > current 40), so output should rise
    out = pid.update(current_value=40.0, dt=1.0)
    assert out > 0.0
    assert out <= 10.0

def test_virtual_plc_closed_loop():
    plc = VirtualPLC()
    history = plc.run_control_loop(
        aluminum_mass_kg=0.2,
        water_mass_kg=1.0,
        target_temp_c=65.0,
        simulation_time_s=10.0,
        dt=1.0
    )
    assert len(history) > 0
    assert "temperature_c" in history[0]
    assert history[-1]["conversion_fraction"] > 0.0

def test_signal_filters():
    filter_tool = SignalFilter()
    filter_tool.reset_kalman(initial_value=25.0)
    
    # Kalman filter smoothing step
    filtered_val = filter_tool.apply_kalman_step(measurement=30.0)
    assert filtered_val > 25.0
    assert filtered_val < 30.0  # Must be smoothed
    
    # Moving average window step
    raw_signals = [1.0, 2.0, 3.0, 4.0, 5.0]
    smoothed = SignalFilter.apply_moving_average(raw_signals, window_size=3)
    assert len(smoothed) == len(raw_signals)
    assert smoothed[-1] == pytest.approx(4.0)

def test_safety_analyzer():
    analyzer = AWRSafetyAnalyzer(room_volume_m3=20.0, ach=5.0)
    # Room LEL check
    res = analyzer.calculate_room_h2_concentration(h2_leak_rate_slpm=10.0)
    assert "concentration_vol_pct" in res
    assert res["concentration_vol_pct"] > 0.0
    
    # Reactor hazard limits
    haz = analyzer.evaluate_reactor_hazards(current_temp_c=98.0, dT_dt_c_s=0.1, current_pressure_bar=5.0, design_pressure_bar=10.0)
    assert haz["esd_active"] is True
    assert "CRITICAL_THERMAL_RUNAWAY_LIMIT_EXCEEDED" in haz["active_warnings"]

def test_regulatory_calcs():
    asme = ASMEPressureVesselCalc()
    res = asme.calculate_thicknesses(
        design_pressure_bar=10.0,
        inside_radius_mm=100.0,
        allowable_stress_mpa=138.0,
        joint_efficiency=0.85,
        corrosion_allowance_mm=1.5
    )
    assert res["calculated_shell_thickness_mm"] > 1.5
    assert res["calculated_head_thickness_mm"] > 1.5
    
    iso = ISO16110Compliance()
    res_iso = iso.evaluate_compliance(
        system_efficiency=0.55,
        has_auto_shutoff=True,
        has_pressure_relief=True,
        has_leak_detection=True,
        max_operating_pressure_bar=5.0
    )
    assert res_iso["iso_16110_compliant"] is True

def test_report_generation():
    from reacton.compliance.reporting import ComplianceReportGenerator
    gen = ComplianceReportGenerator()
    rep = gen.generate_markdown_report(
        sim_summary={"final_conversion_fraction": 0.96, "max_temperature_c": 75.0, "max_pressure_bar": 5.0, "total_hydrogen_produced_g": 50.0},
        asme_results={"vessel_inside_diameter_mm": 200.0, "allowable_stress_psi": 20000.0, "calculated_shell_thickness_mm": 3.5, "calculated_head_thickness_mm": 4.2},
        iso_results={"iso_16110_compliant": True, "standard_reference": "ISO 16110", "active_violations": []},
        efficiency_results={"lhv_system_efficiency": 0.52, "hhv_system_efficiency": 0.61, "second_law_exergy_efficiency": 0.45, "volumetric_capacity_g_h2_l": 12.5, "gravimetric_feedstock_capacity_wt": 11.2, "gravimetric_system_capacity_wt": 2.2},
        co2_results={"co2_saved_vs_smr_kg": 4.5, "co2_saved_vs_coal_grid_kg": 9.0}
    )
    assert "# ASRHÜR REACTON ENGINEERING COMPLIANCE REPORT" in rep
    assert "96.00%" in rep
    assert "3.500 mm" in rep

def test_visualization_mocked(tmp_path):
    import pandas as pd
    from reacton.utils.visualization import ReactorVisualizer
    df = pd.DataFrame([{
        "time_s": 0.0, "temperature_c": 25.0, "pressure_bar": 1.0, "H2_produced_g": 0.0
    }, {
        "time_s": 60.0, "temperature_c": 75.0, "pressure_bar": 5.0, "H2_produced_g": 50.0
    }])
    
    # Save files to temp directory
    p1 = str(tmp_path / "plot1.png")
    p2 = str(tmp_path / "plot2.png")
    p3 = str(tmp_path / "plot3.png")
    
    # Run visualization plots
    ReactorVisualizer.plot_reaction_profile(df, save_path=p1)
    
    pid_hist = [
        {"time_s": 0.0, "temperature_c": 25.0, "setpoint_c": 75.0, "coolant_flow_l_min": 0.0},
        {"time_s": 60.0, "temperature_c": 75.0, "setpoint_c": 75.0, "coolant_flow_l_min": 2.0}
    ]
    ReactorVisualizer.plot_pid_performance(pid_hist, save_path=p2)
    
    fc_hist = [
        {"current_amps": 0.0, "cell_voltage_v": 1.15, "power_output_w": 0.0},
        {"current_amps": 10.0, "cell_voltage_v": 0.85, "power_output_w": 8.5}
    ]
    ReactorVisualizer.plot_polarization_curve(fc_hist, save_path=p3)
    
    import os
    assert os.path.exists(p1)
    assert os.path.exists(p2)
    assert os.path.exists(p3)

def test_structured_logger(capsys):
    from reacton.utils.logging import StructuredLogger
    logger = StructuredLogger("TEST_COMP")
    logger.info("Info message", {"key": "val"})
    logger.warning("Warn message")
    logger.error("Err message")
    logger.critical("Crit message")
    
    captured = capsys.readouterr()
    assert "Info message" in captured.out
    assert "TEST_COMP" in captured.out
    assert "Warn message" in captured.out

def test_unit_converters():
    from reacton.utils.data_processing import UnitConverter
    # bar to Pa and back
    pa = UnitConverter.bar_to_pascal(5.0)
    assert pa == 500000.0
    bar = UnitConverter.pascal_to_bar(500000.0)
    assert bar == 5.0
    
    # SLPM to g/s
    gs = UnitConverter.slpm_to_g_s(10.0)
    slpm = UnitConverter.g_s_to_slpm(gs)
    assert slpm == pytest.approx(10.0)
    
    # kWh and Joules
    j = UnitConverter.kwh_to_joules(1.0)
    assert j == 3.6e6
    kwh = UnitConverter.joules_to_kwh(3.6e6)
    assert kwh == 1.0
