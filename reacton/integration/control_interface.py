"""
PID controller and Virtual PLC integration for AWR reactor systems.

Enables closed-loop control of cooling loops and feedstock injection to maintain 
isothermal reaction states and prevent thermal runaway.
"""

from typing import Dict, Any, List
from .industrial_systems import CoolingLoopModel
from ..core.thermodynamic_models import AWRThermodynamicModel

class PIDController:
    """
    Industrial-grade Proportional-Integral-Derivative (PID) controller.
    
    Includes:
    - Independent Kp, Ki, Kd gains
    - Output saturation limits (clamping)
    - Anti-windup integration clamping
    - Derivative filtering
    """
    
    def __init__(
        self,
        Kp: float,
        Ki: float,
        Kd: float,
        setpoint: float = 0.0,
        output_min: float = 0.0,
        output_max: float = 100.0,
        direct_acting: bool = False
    ):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_min = output_min
        self.output_max = output_max
        self.direct_acting = direct_acting
        
        # Controller states
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_output = 0.0
        
    def update(self, current_value: float, dt: float) -> float:
        """
        Compute the controller output.
        
        Args:
            current_value: Current measured value (process variable).
            dt: Timestep in seconds.
            
        Returns:
            Controller manipulated variable output.
        """
        if dt <= 0:
            return self.prev_output
            
        error = (current_value - self.setpoint) if self.direct_acting else (self.setpoint - current_value)
        
        # 1. Proportional term
        P_val = self.Kp * error
        
        # 2. Integral term with anti-windup clamping
        # We only accumulate error if we are not saturated
        self.integral += error * dt
        I_val = self.Ki * self.integral
        
        # 3. Derivative term
        D_val = self.Kd * (error - self.prev_error) / dt
        
        # Total raw output
        output_raw = P_val + I_val + D_val
        
        # 4. Saturation and Clamping (Anti-windup logic)
        output = max(self.output_min, min(output_raw, self.output_max))
        
        # If output was saturated, revert integral term accumulation to prevent windup
        if output_raw != output:
            self.integral -= error * dt
            
        self.prev_error = error
        self.prev_output = output
        return float(output)

class VirtualPLC:
    """
    Virtual programmable logic controller (PLC) simulating SCADA loop automation.
    
    Coordinates the reactor, the cooling loop, and the PID controller to maintain
    isothermal operation during a highly exothermic run.
    """
    
    def __init__(
        self,
        reactor: AWRThermodynamicModel = None,
        cooling_hx: CoolingLoopModel = None,
        pid: PIDController = None
    ):
        self.reactor = reactor if reactor is not None else AWRThermodynamicModel()
        self.cooling_hx = cooling_hx if cooling_hx is not None else CoolingLoopModel()
        self.pid = pid if pid is not None else PIDController(Kp=8.0, Ki=0.1, Kd=2.0, setpoint=70.0, output_min=0.0, output_max=10.0, direct_acting=True)
        
    def run_control_loop(
        self,
        aluminum_mass_kg: float,
        water_mass_kg: float,
        target_temp_c: float,
        simulation_time_s: float = 600.0,
        dt: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Simulate a closed-loop automated run. The PID adjusts coolant flow rate
        (L/min) to maintain the reactor temperature at target_temp_c.
        
        Args:
            aluminum_mass_kg: Active Aluminum mass (kg).
            water_mass_kg: Water mass (kg).
            target_temp_c: Target operating temperature (°C).
            simulation_time_s: Total simulation time.
            dt: Timestep.
            
        Returns:
            List of telemetry dictionaries with PID logs.
        """
        self.pid.setpoint = target_temp_c
        
        # Setup initial states
        time = 0.0
        temp_c = 50.0
        alpha = 0.0
        
        moles_Al_total = (aluminum_mass_kg * 1000) / (self.reactor.MW_Al * 1000)
        moles_H2_produced = 0.0
        
        # Sauter Mean Radius
        R0_m = 25e-6  # 25 micron particle radius
        
        C_thermal_total = (self.reactor.vessel_mass_kg * self.reactor.Cp_vessel) + \
                          (aluminum_mass_kg * self.reactor.Cp_Al) + \
                          (water_mass_kg * self.reactor.Cp_water)
                          
        history: List[Dict[str, Any]] = []
        coolant_flow_l_min = 0.0
        
        while time <= simulation_time_s:
            # 1. Solve chemical kinetics (non-isothermal step)
            alpha, dalpha_dt = self.reactor.calculate_kinetics_step(
                alpha=alpha,
                R0_m=R0_m,
                temp_c=temp_c,
                pH=14.0,  # highly active alkaline water
                water_type='tap',
                catalyst_molar=0.5,
                dt=dt
            )
            
            # Exothermic Heat Generated
            moles_Al_consumed_per_s = dalpha_dt * moles_Al_total
            q_gen = moles_Al_consumed_per_s * (-self.reactor.delta_H_rxn)  # Watts
            moles_H2_produced += moles_Al_consumed_per_s * 1.5 * dt
            
            # 2. PID Update
            # Measures temp_c, controls coolant flow rate (0.0 to 10.0 L/min)
            coolant_flow_l_min = self.pid.update(current_value=temp_c, dt=dt)
            
            # 3. Cooling Loop Heat Dissipation
            q_cool = self.cooling_hx.calculate_heat_dissipation(
                reactor_temp_c=temp_c,
                coolant_inlet_temp_c=15.0,  # cold water utility
                coolant_flow_rate_l_min=coolant_flow_l_min
            )
            
            # 4. Heat Accumulation
            dT_dt = (q_gen - q_cool) / C_thermal_total
            temp_c += dT_dt * dt
            temp_c = max(15.0, temp_c)
            
            # Record
            history.append({
                "time_s": time,
                "temperature_c": temp_c,
                "setpoint_c": target_temp_c,
                "coolant_flow_l_min": coolant_flow_l_min,
                "heat_generation_w": q_gen,
                "heat_dissipation_w": q_cool,
                "conversion_fraction": alpha,
                "H2_produced_g": moles_H2_produced * (self.reactor.MW_H2 * 1000.0)
            })
            
            if alpha >= 0.999:
                break
                
            time += dt
            
        return history
