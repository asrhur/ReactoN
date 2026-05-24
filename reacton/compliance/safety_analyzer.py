"""
Safety analysis and hazard detection for AWR reactors.

Analyzes LEL concentrations, thermal runaway trajectories, overpressurization, 
and air/O2 ingress hazards.
"""

from typing import Dict, Any

class AWRSafetyAnalyzer:
    """
    Automated safety compliance and warning analyzer for AWR reactors.
    
    Evaluates:
    1. Steady-state hydrogen concentration in ventilated enclosures (LEL limits).
    2. Thermal runaway criteria (T > 95°C or dT/dt > 2.5 °C/s).
    3. Mechanical pressure limits.
    4. Safety alerts and Emergency Shutdown (ESD) signals.
    """
    
    # Hydrogen limits in air
    LEL_vol_pct = 4.0   # Lower Explosive Limit (4.0% vol)
    UEL_vol_pct = 75.0  # Upper Explosive Limit (75.0% vol)
    
    # Reactor safety limits
    T_runaway_limit = 95.0       # Thermal runaway ceiling (°C)
    dT_dt_runaway_limit = 2.5   # Dangerous thermal rise rate (°C/s)
    
    def __init__(self, room_volume_m3: float = 50.0, ach: float = 6.0):
        """
        Initialize Safety Analyzer.
        
        Args:
            room_volume_m3: Volume of the enclosure/room where the reactor is located.
            ach: Air Changes per Hour (ventilation rate).
        """
        self.room_volume_m3 = room_volume_m3
        self.ach = ach
        
    def calculate_room_h2_concentration(self, h2_leak_rate_slpm: float) -> Dict[str, Any]:
        """
        Calculate steady-state hydrogen concentration in the room based on leakage rates.
        
        Formula:
        Q_vent = ACH * V_room / 60 (standard L/min)
        C_ss = Q_leak / (Q_vent + Q_leak) * 100 (%)
        
        Args:
            h2_leak_rate_slpm: Hydrogen leak rate in standard liters per minute.
            
        Returns:
            Dict containing concentration percentage and safety status.
        """
        # Convert ACH to L/min
        # room volume in liters = room_volume_m3 * 1000
        vol_l = self.room_volume_m3 * 1000.0
        q_vent_l_min = (self.ach * vol_l) / 60.0
        
        if h2_leak_rate_slpm <= 0:
            return {"concentration_vol_pct": 0.0, "status": "SAFE", "lel_fraction": 0.0}
            
        c_ss = h2_leak_rate_slpm / (q_vent_l_min + h2_leak_rate_slpm) * 100.0
        lel_fraction = c_ss / self.LEL_vol_pct
        
        status = "SAFE"
        if c_ss >= self.LEL_vol_pct:
            status = "DANGER_LEL_EXCEEDED"
        elif c_ss >= 0.25 * self.LEL_vol_pct:
            status = "WARNING_25_PCT_LEL"
            
        return {
            "concentration_vol_pct": float(c_ss),
            "status": status,
            "lel_fraction": float(lel_fraction)
        }

    def evaluate_reactor_hazards(
        self,
        current_temp_c: float,
        dT_dt_c_s: float,
        current_pressure_bar: float,
        design_pressure_bar: float
    ) -> Dict[str, Any]:
        """
        Run real-time safety checks on reactor temperature and pressure dynamics.
        
        Args:
            current_temp_c: Reactor core temperature.
            dT_dt_c_s: Rate of temperature change.
            current_pressure_bar: Reactor internal pressure.
            design_pressure_bar: Vessel maximum design pressure.
            
        Returns:
            Dict containing ESD status, warnings, and active mitigation steps.
        """
        esd_triggered = False
        warnings = []
        mitigation_actions = []
        
        # 1. Thermal Runaway checks
        if current_temp_c >= self.T_runaway_limit:
            esd_triggered = True
            warnings.append("CRITICAL_THERMAL_RUNAWAY_LIMIT_EXCEEDED")
            mitigation_actions.append("EMERGENCY_COOLING_VALVE_MAX_OPEN")
            mitigation_actions.append("STOP_ALUMINUM_FEED")
        elif dT_dt_c_s >= self.dT_dt_runaway_limit:
            esd_triggered = True
            warnings.append("CRITICAL_TEMPERATURE_RISE_RATE_EXCEEDED")
            mitigation_actions.append("EMERGENCY_COOLING_VALVE_MAX_OPEN")
            mitigation_actions.append("STOP_ALUMINUM_FEED")
        elif current_temp_c >= 0.85 * self.T_runaway_limit:
            warnings.append("HIGH_TEMPERATURE_WARNING")
            mitigation_actions.append("INCREASE_COOLING_FLOW")
            
        # 2. Overpressure checks
        if current_pressure_bar >= design_pressure_bar:
            esd_triggered = True
            warnings.append("CRITICAL_OVERPRESSURE_LIMIT_EXCEEDED")
            mitigation_actions.append("OPEN_RELEIF_SAFETY_VALVE")
            mitigation_actions.append("STOP_ALUMINUM_FEED")
        elif current_pressure_bar >= 0.8 * design_pressure_bar:
            warnings.append("HIGH_PRESSURE_WARNING")
            mitigation_actions.append("VAPOR_VENT_SOLENOID_OPEN")
            
        status = "ESD_ACTIVE" if esd_triggered else ("WARNING_ACTIVE" if len(warnings) > 0 else "OPERATIONAL")
        
        return {
            "esd_active": esd_triggered,
            "system_status": status,
            "active_warnings": warnings,
            "mitigation_actions": mitigation_actions
        }
