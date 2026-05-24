"""
ASME and ISO regulatory compliance calculators for AWR reactors.

Implements structural vessel wall sizing based on ASME BPVC Section VIII Division 1 
standards and checks system configuration against ISO 16110 hydrogen generator metrics.
"""

from typing import Dict, Any

class ASMEPressureVesselCalc:
    """
    ASME BPVC Section VIII Division 1 Pressure Vessel design compliance engine.
    
    Provides:
    - Cylindrical shell minimum wall thickness
    - 2:1 Ellipsoidal head minimum wall thickness
    """
    
    def __init__(self):
        pass
        
    def calculate_thicknesses(
        self,
        design_pressure_bar: float,
        inside_radius_mm: float,
        allowable_stress_mpa: float = 138.0,
        joint_efficiency: float = 0.85,
        corrosion_allowance_mm: float = 1.5
    ) -> Dict[str, float]:
        """
        Calculate vessel component thicknesses using standard ASME Sec VIII Div 1 rules.
        
        Shell formula:
        t = (P * R) / (S * E - 0.6 * P) + C_a
        
        Head formula (2:1 Ellipsoidal):
        t = (P * D) / (2 * S * E - 0.2 * P) + C_a
        
        Note: P, S must be in consistent units (e.g. psi or MPa). We convert all to MPa.
        1 bar = 0.1 MPa.
        
        Args:
            design_pressure_bar: Vessel design pressure (gauge) in bar.
            inside_radius_mm: Inside radius of vessel shell in mm.
            allowable_stress_mpa: Maximum allowable material stress in MPa (typical 316SS = 138 MPa).
            joint_efficiency: Weld joint efficiency (0.7 to 1.0, default 0.85).
            corrosion_allowance_mm: Extra wall thickness added for corrosion in mm.
            
        Returns:
            Dict containing calculated thicknesses.
        """
        # Convert bar to MPa
        P_mpa = design_pressure_bar * 0.1
        
        # Calculate cylindrical shell thickness
        # t_s = (P * R) / (S * E - 0.6 * P)
        denom_s = (allowable_stress_mpa * joint_efficiency) - (0.6 * P_mpa)
        
        if denom_s <= 0:
            # Material stress is too low or pressure is too high, shell will rupture
            t_shell = 999.0
        else:
            t_shell = (P_mpa * inside_radius_mm) / denom_s + corrosion_allowance_mm
            
        # Calculate ellipsoidal head thickness (2:1 ratio)
        # Inside Diameter
        D_mm = 2.0 * inside_radius_mm
        denom_h = (2.0 * allowable_stress_mpa * joint_efficiency) - (0.2 * P_mpa)
        
        if denom_h <= 0:
            t_head = 999.0
        else:
            t_head = (P_mpa * D_mm) / denom_h + corrosion_allowance_mm
            
        # Convert allowable stress to traditional PSI for reference
        stress_psi = allowable_stress_mpa * 145.0377
        
        return {
            "vessel_inside_diameter_mm": float(D_mm),
            "allowable_stress_psi": float(stress_psi),
            "calculated_shell_thickness_mm": float(t_shell),
            "calculated_head_thickness_mm": float(t_head)
        }

class ISO16110Compliance:
    """
    Evaluates reactor platform compliance with ISO 16110:
    "Hydrogen generators using fuel processing technologies".
    """
    
    def __init__(self):
        pass
        
    def evaluate_compliance(
        self,
        system_efficiency: float,
        has_auto_shutoff: bool,
        has_pressure_relief: bool,
        has_leak_detection: bool,
        max_operating_pressure_bar: float
    ) -> Dict[str, Any]:
        """
        Evaluate and return an ISO 16110 safety compliance scorecard.
        """
        passed = True
        failures = []
        
        # ISO 16110 requires minimum efficiency of 45% for industrial fuel processors
        if system_efficiency < 0.45:
            passed = False
            failures.append("EFFICIENCY_BELOW_ISO_MINIMUM_45_PCT")
            
        # Safety critical shutoffs are MANDATORY
        if not has_auto_shutoff:
            passed = False
            failures.append("MANDATORY_AUTOMATED_SHUTOFF_MISSING")
            
        if not has_pressure_relief:
            passed = False
            failures.append("MANDATORY_PRESSURE_RELIEF_VALVE_MISSING")
            
        # Leak detection required for indoor operations at high pressures (>2 bar)
        if max_operating_pressure_bar > 2.0 and not has_leak_detection:
            passed = False
            failures.append("MANDATORY_GAS_LEAK_DETECTION_MISSING")
            
        status = "COMPLIANT" if passed else "NON_COMPLIANT"
        
        return {
            "iso_16110_compliant": passed,
            "compliance_status": status,
            "active_violations": failures,
            "standard_reference": "ISO 16110-1:2007 (Hydrogen generators using fuel processing)"
        }
