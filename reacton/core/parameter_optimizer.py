"""
Multivariable parameter optimization for AWR system.

Utilizes scipy.optimize to solve for optimal operational settings under safety, 
purity, and mechanical stress constraints.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, Any, List, Tuple
from .thermodynamic_models import AWRThermodynamicModel

class AWRParameterOptimizer:
    """
    Non-linear multivariable parameter optimizer for AWR reactors.
    
    Optimizes:
    - Aluminum feed rate (g/min)
    - Water-to-Al molar ratio (excess stoichiometric factor)
    - Catalyst (NaOH/KOH) concentration (M)
    - Reactor pressure (bar)
    - Condenser temperature (°C)
    
    Objectives:
    - Maximize H2 flow rate (SLPM)
    - Minimize Levelized Cost of Hydrogen (LCOH, $/kg-H2)
    - Maximize thermodynamic exergy efficiency
    """
    
    def __init__(self, model: AWRThermodynamicModel = None):
        """
        Initialize the parameter optimizer.
        
        Args:
            model: Instance of AWRThermodynamicModel.
        """
        self.model = model if model is not None else AWRThermodynamicModel()
        
        # Financial cost constants for LCOH calculation ($/kg)
        self.cost_Al_premium = 2.80     # Premium Al powder
        self.cost_Al_recycled = 1.10    # Recycled scrap/dross
        self.cost_catalyst_pure = 1.50  # NaOH catalyst
        self.cost_water = 0.002         # Industrial water
        self.cost_cooling_kwh = 0.08    # Electrical power for chilling
        
    def _calculate_lcoh(
        self,
        feed_rate: float,
        water_ratio: float,
        catalyst_m: float,
        pressure_bar: float,
        condenser_t: float,
        feedstock_type: str,
        h2_yield_g: float,
        cooling_duty_w: float
    ) -> float:
        """
        Helper to compute Levelized Cost of Hydrogen (LCOH) in $/kg-H2.
        """
        # Mass flow rate of Al (kg/h)
        m_dot_Al = (feed_rate * 60.0) / 1000.0
        
        # Select feedstock price
        cost_Al = self.cost_Al_recycled if feedstock_type == 'recycled' else self.cost_Al_premium
        
        # Al moles/hr
        n_dot_Al = (m_dot_Al * 1000.0) / (self.model.MW_Al * 1000.0)
        
        # Water required (moles/hr)
        n_dot_H2O = n_dot_Al * water_ratio
        m_dot_H2O = (n_dot_H2O * self.model.MW_H2O) / 1000.0  # kg/h
        
        # Catalyst mass in liquid volume (1 L water ~ 55.5 moles)
        # Liters of water = m_dot_H2O (since density ~ 1kg/L)
        m_dot_cat = m_dot_H2O * catalyst_m * 0.040  # NaOH molar mass = 40 g/mol = 0.04 kg/mol
        
        # Energy expense for condenser chilling (cooling duty converted to electrical consumption, COP ~ 3.0)
        chilling_kw = (cooling_duty_w / 1000.0) / 3.0
        cost_chilling_hr = chilling_kw * self.cost_cooling_kwh
        
        # Hourly expenses
        cost_hourly = (m_dot_Al * cost_Al) + \
                      (m_dot_H2O * self.cost_water) + \
                      (m_dot_cat * self.cost_catalyst_pure) + \
                      cost_chilling_hr
                      
        # H2 generated per hour (kg/hr)
        # Yield is modeled based on conversion efficiency and stoichiometry
        # 1 kg Al produces 3*2.016 / (2*26.98) = 0.112 kg H2 at 100% yield
        h2_kg_per_hr = m_dot_Al * 0.112 * 0.96  # 96% efficiency
        
        if h2_kg_per_hr <= 0:
            return 9999.0
            
        lcoh = cost_hourly / h2_kg_per_hr
        return float(lcoh)

    def optimize(
        self,
        objective: str = 'maximize_h2_rate',
        feedstock_type: str = 'premium',
        water_type: str = 'tap',
        target_purity: float = 0.999,
        max_pressure_bar: float = 16.0,
        max_temp_c: float = 95.0
    ) -> Dict[str, Any]:
        """
        Perform multivariable optimization for the AWR system using SciPy.
        
        Variables vector x:
        x[0]: Aluminum Feed Rate (g/min) - Range: [1.0, 50.0]
        x[1]: Water-to-Al Molar Ratio - Range: [3.0, 10.0]
        x[2]: Catalyst Molarity (M) - Range: [0.0, 4.0]
        x[3]: Reactor Operating Pressure (bar) - Range: [1.0, max_pressure_bar]
        x[4]: Condenser Temperature (°C) - Range: [2.0, 35.0]
        
        Args:
            objective: 'maximize_h2_rate', 'minimize_lcoh', or 'maximize_exergy'.
            feedstock_type: 'premium' or 'recycled'.
            water_type: 'pure', 'tap', or 'sea'.
            target_purity: Desired minimum hydrogen purity (0.0 to 1.0).
            max_pressure_bar: Maximum design/allowable pressure.
            max_temp_c: Maximum safety shutdown temperature.
            
        Returns:
            Dictionary containing optimal variables, objective value, and status metrics.
        """
        
        # Initial guess (x0)
        # [feed_rate, water_ratio, catalyst_m, pressure_bar, condenser_t]
        init_pressure = 8.0 if target_purity > 0.99 else 5.0
        init_condenser = 5.0 if target_purity > 0.99 else 15.0
        x0 = np.array([10.0, 4.0, 1.0, init_pressure, init_condenser])
        
        # Bounds on decision variables
        bounds = [
            (1.0, 50.0),            # feed_rate, g/min
            (3.0, 10.0),            # water_ratio
            (0.0, 4.0),             # catalyst_m, M
            (1.0, max_pressure_bar), # pressure_bar
            (2.0, 35.0)             # condenser_t, °C
        ]
        
        # Nonlinear constraints
        # 1. Purity Constraint: y_H2 >= target_purity
        # y_H2 = (P - P_sat(T_cond)) / P
        def purity_constraint(x):
            pressure = x[3]
            condenser_t = x[4]
            p_sat = self.model.calculate_antoine_vapor_pressure(condenser_t)
            y_h2 = (pressure - p_sat) / pressure
            return y_h2 - target_purity  # Must be >= 0
            
        # 2. Temperature safety check (Simplified steady-state thermal approximation)
        # Q_gen = n_dot_Al * delta_H_rxn
        # T_rxn = T_ambient + Q_gen / (cooling_duty)
        # We constrain it to stay below max_temp_c.
        def thermal_constraint(x):
            feed_rate = x[0]
            catalyst_m = x[2]
            # Moles of Al per second
            mol_al_sec = (feed_rate / 60.0) / (self.model.MW_Al * 1000.0)
            q_gen = mol_al_sec * (-self.model.delta_H_rxn)  # Watts
            
            # Simple reactor thermal heat dissipation parameter
            dissipation_coeff = 25.0  # W/K (reactor design coefficient)
            cooling_w = 400.0  # reference cooling duty (W)
            temp_est = 25.0 + (q_gen / (dissipation_coeff + (catalyst_m * 10.0)))
            return max_temp_c - temp_est  # Must be >= 0
            
        constraints = [
            {'type': 'ineq', 'fun': purity_constraint},
            {'type': 'ineq', 'fun': thermal_constraint}
        ]
        
        # Define objective functions to MINIMIZE (SciPy is a minimizer)
        if objective == 'maximize_h2_rate':
            def obj_fun(x):
                feed_rate = x[0]
                catalyst_m = x[2]
                pressure = x[3]
                
                # Yield scales with active Al feeding, activation kinetics (catalyst), and pressure feedback
                purity = (pressure - self.model.calculate_antoine_vapor_pressure(x[4])) / pressure
                purity = max(0.0, min(purity, 1.0))
                
                # SLPM = (g/min / MW_Al) * 1.5 * 22.4 (molar volume at STP) * purity
                slpm = (feed_rate / (self.model.MW_Al * 1000.0)) * 1.5 * 22.414 * purity
                
                # Apply kinetic rate penalty based on catalyst molarity (reaction slows if catalyst is too low)
                rate_penalty = 1.0 - np.exp(-1.5 * (catalyst_m + 0.1))
                return -slpm * rate_penalty  # Negated to maximize
                
        elif objective == 'minimize_lcoh':
            def obj_fun(x):
                feed_rate = x[0]
                water_ratio = x[1]
                catalyst_m = x[2]
                pressure = x[3]
                condenser_t = x[4]
                
                # Simple approximation of active cooling duty
                cooling_w = (feed_rate / 60.0) * 1e-3 * 16.7e6 * 0.35  # dissipating 35% of reaction enthalpy
                
                lcoh = self._calculate_lcoh(
                    feed_rate=feed_rate,
                    water_ratio=water_ratio,
                    catalyst_m=catalyst_m,
                    pressure_bar=pressure,
                    condenser_t=condenser_t,
                    feedstock_type=feedstock_type,
                    h2_yield_g=feed_rate * 0.112,
                    cooling_duty_w=cooling_w
                )
                return lcoh
                
        elif objective == 'maximize_exergy':
            def obj_fun(x):
                # Exergy efficiency: Ex_H2 / (Ex_Al + Ex_Water + Work_cool)
                # Maximize this ratio -> minimize its negative
                feed_rate = x[0]
                catalyst_m = x[2]
                pressure = x[3]
                
                # Entropy generation scales with high temperature gradients (catalyst-driven heat)
                # and compression requirements.
                ex_eff = 0.72 - (0.02 * catalyst_m) - (0.01 * (pressure - 5.0)**2 / max_pressure_bar)
                ex_eff = max(0.2, min(ex_eff, 0.95))
                return -ex_eff
                
        else:
            raise ValueError(f"Unknown objective: {objective}")
            
        # Execute optimization
        res = minimize(
            fun=obj_fun,
            x0=x0,
            bounds=bounds,
            constraints=constraints,
            method='SLSQP',
            options={'ftol': 1e-6, 'maxiter': 200}
        )
        
        # Format results
        opt_x = res.x
        
        # Calculate derived metrics
        opt_feed_rate = float(opt_x[0])
        opt_water_ratio = float(opt_x[1])
        opt_catalyst_m = float(opt_x[2])
        opt_pressure = float(opt_x[3])
        opt_condenser_t = float(opt_x[4])
        
        p_sat = self.model.calculate_antoine_vapor_pressure(opt_condenser_t)
        resulting_purity = float((opt_pressure - p_sat) / opt_pressure)
        
        h2_flow_slpm = (opt_feed_rate / (self.model.MW_Al * 1000.0)) * 1.5 * 22.414 * resulting_purity
        h2_flow_slpm *= (1.0 - np.exp(-1.5 * (opt_catalyst_m + 0.1)))
        
        cooling_est_w = (opt_feed_rate / 60.0) * 1e-3 * 16.7e6 * 0.35
        
        resulting_lcoh = self._calculate_lcoh(
            feed_rate=opt_feed_rate,
            water_ratio=opt_water_ratio,
            catalyst_m=opt_catalyst_m,
            pressure_bar=opt_pressure,
            condenser_t=opt_condenser_t,
            feedstock_type=feedstock_type,
            h2_yield_g=opt_feed_rate * 0.112,
            cooling_duty_w=cooling_est_w
        )
        
        exergy_eff = 0.72 - (0.02 * opt_catalyst_m) - (0.01 * (opt_pressure - 5.0)**2 / max_pressure_bar)
        
        return {
            "success": bool(res.success),
            "status_message": str(res.message),
            "optimal_parameters": {
                "feed_rate_g_min": opt_feed_rate,
                "water_to_al_molar_ratio": opt_water_ratio,
                "catalyst_molarity_M": opt_catalyst_m,
                "reactor_pressure_bar": opt_pressure,
                "condenser_temp_c": opt_condenser_t
            },
            "metrics": {
                "hydrogen_flow_rate_slpm": float(h2_flow_slpm),
                "hydrogen_purity": float(resulting_purity),
                "levelized_cost_usd_kg": float(resulting_lcoh),
                "estimated_exergy_efficiency": float(ex_eff if objective == 'maximize_exergy' else exergy_eff),
                "estimated_cooling_duty_w": float(cooling_est_w)
            }
        }
