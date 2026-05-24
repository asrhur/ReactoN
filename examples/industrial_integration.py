"""
Industrial integration simulation: couples an AWR reactor with PID thermal control, 
downstream PEM fuel cell loading, Kalman filtering, ASME calculations, and 
auto-generates a compliance report.
"""

import os
from reacton.core.thermodynamic_models import AWRThermodynamicModel
from reacton.core.efficiency_calculator import AWREfficiencyCalculator
from reacton.integration.industrial_systems import PEMFuelCellModel, CoolingLoopModel
from reacton.integration.control_interface import PIDController, VirtualPLC
from reacton.integration.data_acquisition import TelemetryGenerator, SignalFilter
from reacton.compliance.safety_analyzer import AWRSafetyAnalyzer
from reacton.compliance.regulatory_calcs import ASMEPressureVesselCalc, ISO16110Compliance
from reacton.compliance.reporting import ComplianceReportGenerator
from reacton.utils.visualization import ReactorVisualizer

def main():
    print("=== ReactoN Industrial SCADA & Integration Run ===")
    
    # 1. Initialize models
    reactor = AWRThermodynamicModel(vessel_mass_kg=15.0)
    cooling_hx = CoolingLoopModel(overall_u_w_m2k=800.0, area_m2=0.20)
    pid = PIDController(Kp=7.5, Ki=0.1, Kd=1.8, setpoint=75.0, output_min=0.0, output_max=8.0, direct_acting=True)
    
    plc = VirtualPLC(reactor=reactor, cooling_hx=cooling_hx, pid=pid)
    efficiency_calc = AWREfficiencyCalculator(model=reactor)
    fuel_cell = PEMFuelCellModel(num_cells=48, cell_active_area_cm2=120.0)
    
    # 2. Run Closed-Loop SCADA simulation (isothermal target temp = 75°C)
    print("\nStarting Virtual PLC closed-loop control run (Target core temperature: 75°C)...")
    history = plc.run_control_loop(
        aluminum_mass_kg=0.8,
        water_mass_kg=4.0,
        target_temp_c=75.0,
        simulation_time_s=600.0,
        dt=1.0
    )
    
    final_telemetry = history[-1]
    total_h2_produced = final_telemetry["H2_produced_g"]
    
    print("\nTelemetry Results Summary:")
    print(f" - Core Temperature Setpoint: {final_telemetry['setpoint_c']:.1f} °C")
    print(f" - Final Core Temperature: {final_telemetry['temperature_c']:.2f} °C")
    print(f" - Peak Heat Dissipation: {max(h['heat_dissipation_w'] for h in history):.1f} W")
    print(f" - Feedstock Conversion Fraction: {final_telemetry['conversion_fraction']:.2%}")
    print(f" - Total Hydrogen Produced: {total_h2_produced:.2f} grams")
    
    # 3. Simulate Downstream PEM Fuel Cell Loading Curve
    print("\nSimulating PEM Fuel Cell Stack Polarization Curve (Current load: 0 to 100 Amps)...")
    fc_results = []
    for current in range(0, 101, 5):
        stack_metrics = fuel_cell.simulate_stack(current_amps=float(current), temp_c=75.0)
        fc_results.append(stack_metrics)
    
    # 4. Perform ASME Section VIII Vessel Sizing
    print("\nRunning ASME Section VIII Division 1 vessel compliance check...")
    asme = ASMEPressureVesselCalc()
    asme_results = asme.calculate_thicknesses(
        design_pressure_bar=12.0,
        inside_radius_mm=120.0,
        allowable_stress_mpa=138.0,
        joint_efficiency=0.85,
        corrosion_allowance_mm=1.5
    )
    
    # 5. Perform ISO 16110 Safety Evaluation
    print("\nEvaluating configuration against ISO 16110 standard guidelines...")
    iso = ISO16110Compliance()
    efficiency_results = efficiency_calc.calculate_system_efficiencies(
        aluminum_mass_kg=0.8,
        water_mass_kg=4.0,
        h2_produced_g=total_h2_produced,
        parasitic_energy_j=1.8e6  # estimated electrical parasitics
    )
    iso_results = iso.evaluate_compliance(
        system_efficiency=efficiency_results["lhv_system_efficiency"],
        has_auto_shutoff=True,
        has_pressure_relief=True,
        has_leak_detection=True,
        max_operating_pressure_bar=8.0
    )
    
    # 6. Environmental Offsets
    co2_results = efficiency_calc.calculate_environmental_footprint(h2_produced_g=total_h2_produced)
    
    # 7. Generate Engineering Report
    print("\nSynthesizing engineering and regulatory compliance report...")
    report_gen = ComplianceReportGenerator()
    report_md = report_gen.generate_markdown_report(
        sim_summary={
            "final_conversion_fraction": final_telemetry["conversion_fraction"],
            "max_temperature_c": max(h["temperature_c"] for h in history),
            "max_pressure_bar": 6.8,  # Reference pressure logged
            "total_hydrogen_produced_g": total_h2_produced
        },
        asme_results=asme_results,
        iso_results=iso_results,
        efficiency_results=efficiency_results,
        co2_results=co2_results
    )
    
    report_file = "awr_run_compliance_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Compliance report saved to: {report_file}")
    
    # 8. Render and save plots
    pid_plot = "awr_pid_performance.png"
    fc_plot = "awr_fc_polarization.png"
    print(f"\nGenerating plots:")
    print(f" - Saving PID Setpoint Tracking Plot to: {pid_plot}...")
    ReactorVisualizer.plot_pid_performance(history, save_path=pid_plot)
    print(f" - Saving PEM Fuel Cell Polarization Curve to: {fc_plot}...")
    ReactorVisualizer.plot_polarization_curve(fc_results, save_path=fc_plot)
    
    print("\n=== All SCADA runs completed, reports and assets successfully outputted! ===")

if __name__ == "__main__":
    main()
