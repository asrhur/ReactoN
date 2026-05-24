"""
Example illustrating multiple feedstock grades and water qualities comparison
with levelized cost of hydrogen (LCOH) analysis.
"""

import os
from reacton.core.thermodynamic_models import AWRThermodynamicModel
from reacton.core.parameter_optimizer import AWRParameterOptimizer
from reacton.core.efficiency_calculator import AWREfficiencyCalculator

def main():
    print("=== ReactoN Multi-Feedstock & LCOH Comparative Analysis ===")
    
    model = AWRThermodynamicModel()
    optimizer = AWRParameterOptimizer(model=model)
    efficiency_calc = AWREfficiencyCalculator(model=model)
    
    # Run three distinct operational cases
    cases = [
        {
            "name": "Case A: Premium Pure Al + Pure Water (High purity, PEM stack grade)",
            "objective": "maximize_h2_rate",
            "feedstock": "premium",
            "water": "pure",
            "purity": 0.999
        },
        {
            "name": "Case B: Recycled Scrap + Seawater (Disaster relief, AFAD/TAM field pilot)",
            "objective": "minimize_lcoh",
            "feedstock": "recycled",
            "water": "sea",
            "purity": 0.99
        },
        {
            "name": "Case C: Recycled Scrap + Tap Water (Balanced standard backup utility)",
            "objective": "minimize_lcoh",
            "feedstock": "recycled",
            "water": "tap",
            "purity": 0.995
        }
    ]
    
    for case in cases:
        print(f"\n--- Running: {case['name']} ---")
        res = optimizer.optimize(
            objective=case["objective"],
            feedstock_type=case["feedstock"],
            water_type=case["water"],
            target_purity=case["purity"],
            max_pressure_bar=12.0
        )
        
        if res["success"]:
            p = res["optimal_parameters"]
            m = res["metrics"]
            print("Optimal Settings:")
            print(f" - Aluminum Feed Rate: {p['feed_rate_g_min']:.2f} g/min")
            print(f" - Water-to-Al Molar Ratio: {p['water_to_al_molar_ratio']:.2f}")
            print(f" - Catalyst Concentration: {p['catalyst_molarity_M']:.2f} M")
            print(f" - Reactor Operating Pressure: {p['reactor_pressure_bar']:.2f} bar")
            print(f" - Condenser Temperature: {p['condenser_temp_c']:.2f} °C")
            
            print("\nResulting Metrics:")
            print(f" - Dry Hydrogen Purity: {m['hydrogen_purity']:.4%}")
            print(f" - Hydrogen Flow Rate: {m['hydrogen_flow_rate_slpm']:.2f} SLPM")
            print(f" - Levelized Cost (LCOH): ${m['levelized_cost_usd_kg']:.3f} / kg H2")
            print(f" - Exergy Efficiency: {m['estimated_exergy_efficiency']:.2%}")
            
            # Print CO2 footprint reductions for 10 kg generation
            carbon = efficiency_calc.calculate_environmental_footprint(h2_produced_g=10000.0)
            print(f" - Carbon saved per 10kg H2 vs. SMR: {carbon['co2_saved_vs_smr_kg']:.1f} kg-CO2")
        else:
            print(f"Optimization failed: {res['status_message']}")

if __name__ == "__main__":
    main()
