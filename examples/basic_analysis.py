"""
Basic example demonstrating a single batch AWR reactor run simulation
and plotting the reaction profile.
"""

import os
from reacton.core.thermodynamic_models import AWRThermodynamicModel
from reacton.utils.visualization import ReactorVisualizer

def main():
    print("=== ReactoN AWR Basic Simulation Run ===")
    
    # Initialize thermodynamic model
    model = AWRThermodynamicModel(vessel_mass_kg=12.0)
    
    # Run a batch simulation
    # Inputs: 0.5 kg aluminum, 2.5 kg water, 3nm passive oxide, 20um particles, tap water, pH=12.5, 0.2M catalyst
    print("\nSimulating batch reaction with:")
    print(" - Aluminum feedstock mass: 0.50 kg")
    print(" - Liquid water mass: 2.50 kg")
    print(" - Particle diameter d50: 20.0 microns")
    print(" - Active pH: 14.0")
    
    df = model.simulate_batch_reaction(
        aluminum_mass_kg=0.5,
        water_mass_kg=2.5,
        d_ox_nm=3.0,
        particle_size_mean_um=20.0,
        particle_size_std_um=4.0,
        pH=14.0,
        water_type="tap",
        catalyst_molar=0.2,
        reactor_volume_l=6.0,
        cooling_duty_w=250.0,
        initial_temp_c=50.0,
        dt=1.0,
        max_time_s=3600.0
    )
    
    print(f"\nSimulation finished successfully!")
    print(f"Total time elapsed: {df['time_s'].max() / 60.0:.2f} minutes")
    print(f"Final feedstock conversion fraction: {df['conversion_fraction'].max():.2%}")
    print(f"Maximum temperature reached: {df['temperature_c'].max():.2f} °C")
    print(f"Maximum pressure reached: {df['pressure_bar'].max():.2f} bar")
    print(f"Total hydrogen gas produced: {df['H2_produced_g'].max():.2f} grams")
    
    # Render beautiful visualization
    plot_name = "awr_basic_reaction_profile.png"
    print(f"\nGenerating and saving reaction profile plot to: {plot_name}...")
    ReactorVisualizer.plot_reaction_profile(df, save_path=plot_name)
    print("Plot successfully saved!")

if __name__ == "__main__":
    main()
