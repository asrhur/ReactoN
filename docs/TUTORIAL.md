# ReactoN Developer Quickstart Tutorial

This tutorial guides you through importing and running AWR thermodynamic simulations, parameter optimizations, and mechanical design checks using the **ReactoN** Python package.

---

## 🐍 1. Running a Batch Simulation in Python

```python
from reacton.core.thermodynamic_models import AWRThermodynamicModel
from reacton.utils.visualization import ReactorVisualizer

# 1. Initialize our thermodynamic kinetics engine
model = AWRThermodynamicModel(vessel_mass_kg=12.0)

# 2. Simulate batch reaction under custom inputs
df = model.simulate_batch_reaction(
    aluminum_mass_kg=0.5,
    water_mass_kg=2.5,
    d_ox_nm=3.0,
    particle_size_mean_um=20.0,
    particle_size_std_um=4.0,
    pH=12.5,
    water_type="tap",
    catalyst_molar=0.2,
    reactor_volume_l=6.0,
    cooling_duty_w=250.0
)

# 3. Print final results
print(f"H2 Yield: {df['H2_produced_g'].max():.2f} grams")
print(f"Max Core Temperature: {df['temperature_c'].max():.1f} °C")

# 4. Generate and save a profile chart
ReactorVisualizer.plot_reaction_profile(df, save_path="my_reaction_profile.png")
```

---

## 📈 2. Operational Parameter Optimization

```python
from reacton.core.parameter_optimizer import AWRParameterOptimizer

optimizer = AWRParameterOptimizer()

# Solve for settings that minimize LCOH using recycled scrap in seawater
res = optimizer.optimize(
    objective="minimize_lcoh",
    feedstock_type="recycled",
    water_type="sea",
    target_purity=0.99
)

if res["success"]:
    params = res["optimal_parameters"]
    metrics = res["metrics"]
    print(f"Optimal Feed Rate: {params['feed_rate_g_min']:.2f} g/min")
    print(f"Optimal Pressure: {params['reactor_pressure_bar']:.2f} bar")
    print(f"Resulting LCOH: ${metrics['levelized_cost_usd_kg']:.3f} / kg H2")
```

---

## 🛠️ 3. ASME Section VIII Thickness Sizing

```python
from reacton.compliance.regulatory_calcs import ASMEPressureVesselCalc

asme = ASMEPressureVesselCalc()

# Sizing vessel for 12 bar design pressure
res = asme.calculate_thicknesses(
    design_pressure_bar=12.0,
    inside_radius_mm=120.0,
    allowable_stress_mpa=138.0,
    joint_efficiency=0.85,
    corrosion_allowance_mm=1.5
)

print(f"Required Shell Wall Thickness: {res['calculated_shell_thickness_mm']:.3f} mm")
print(f"Required Head Wall Thickness: {res['calculated_head_thickness_mm']:.3f} mm")
```
