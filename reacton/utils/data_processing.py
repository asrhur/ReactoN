"""
Data processing and unit conversion utilities.
"""

class UnitConverter:
    """
    Standard unit conversions for chemical and mechanical engineering systems.
    """
    
    # H2 density at Standard Temperature & Pressure (0 °C, 1 atm) in g/L
    H2_density_stp_g_l = 0.08988
    
    @staticmethod
    def bar_to_pascal(bar: float) -> float:
        """Convert pressure from bar to Pascals."""
        return float(bar * 1e5)
        
    @staticmethod
    def pascal_to_bar(pa: float) -> float:
        """Convert pressure from Pascals to bar."""
        return float(pa * 1e-5)
        
    @classmethod
    def slpm_to_g_s(cls, slpm: float) -> float:
        """
        Convert Hydrogen volumetric flow rate in Standard Liters Per Minute (SLPM) 
        to mass flow rate in grams per second.
        """
        # slpm * density (g/L) / 60 (s/min)
        return float((slpm * cls.H2_density_stp_g_l) / 60.0)
        
    @classmethod
    def g_s_to_slpm(cls, g_s: float) -> float:
        """
        Convert Hydrogen mass flow rate in grams per second to 
        volumetric flow rate in Standard Liters Per Minute (SLPM).
        """
        if cls.H2_density_stp_g_l <= 0:
            return 0.0
        return float((g_s * 60.0) / cls.H2_density_stp_g_l)
        
    @staticmethod
    def joules_to_kwh(joules: float) -> float:
        """Convert energy from Joules to kilowatt-hours."""
        return float(joules / 3.6e6)
        
    @staticmethod
    def kwh_to_joules(kwh: float) -> float:
        """Convert energy from kilowatt-hours to Joules."""
        return float(kwh * 3.6e6)
