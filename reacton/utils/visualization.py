"""
Beautiful engineering visualizations for AWR reactor analysis.

Generates publication-quality charts for reaction kinetics, PID controller setpoint 
tracking, and PEM fuel cell voltage-current-power characteristics.
"""

import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Any

class ReactorVisualizer:
    """
    Renders clean, beautiful, professional-grade plots using custom styling.
    """
    
    # Modern, premium styling parameters
    primary_color = "#0B3C5D"    # Deep Navy
    secondary_color = "#328CC1"  # Vibrant Cyan/Blue
    accent_color = "#D9B310"     # Warm Gold/Amber
    danger_color = "#D9534F"     # Muted Red
    grid_style = {"color": "#E5E5E5", "linestyle": "--", "linewidth": 0.8}
    
    @classmethod
    def apply_custom_style(cls):
        """Apply modern font and sizing defaults."""
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.edgecolor"] = "#CCCCCC"
        plt.rcParams["axes.linewidth"] = 0.8
        
    @classmethod
    def plot_reaction_profile(cls, df: pd.DataFrame, save_path: str = None):
        """
        Plot temperature, pressure, and hydrogen yield history.
        """
        cls.apply_custom_style()
        fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=300)
        
        time_min = df["time_s"] / 60.0
        
        # Left axis: Temperature and pressure
        color_temp = cls.secondary_color
        ax1.plot(time_min, df["temperature_c"], color=color_temp, linewidth=1.8, label="Core Temp (°C)")
        ax1.set_xlabel("Time (minutes)", fontweight="bold")
        ax1.set_ylabel("Core Temperature (°C)", color=color_temp, fontweight="bold")
        ax1.tick_params(axis="y", labelcolor=color_temp)
        ax1.grid(True, **cls.grid_style)
        
        # Second Left axis (or right axis) for pressure
        ax1_p = ax1.twinx()
        color_press = cls.danger_color
        ax1_p.plot(time_min, df["pressure_bar"], color=color_press, linestyle="--", linewidth=1.5, label="Pressure (bar)")
        ax1_p.set_ylabel("Pressure (bar)", color=color_press, fontweight="bold")
        ax1_p.tick_params(axis="y", labelcolor=color_press)
        # Position second right axis further to make room for H2 yield on right axis
        
        # Right axis: Hydrogen yield
        ax2 = ax1.twinx()
        # Move it to the right side and offset
        ax2.spines["right"].set_position(("axes", 1.15))
        color_yield = cls.primary_color
        ax2.plot(time_min, df["H2_produced_g"], color=color_yield, linewidth=1.8, label="H2 Yield (g)")
        ax2.set_ylabel("Hydrogen Produced (grams)", color=color_yield, fontweight="bold")
        ax2.tick_params(axis="y", labelcolor=color_yield)
        
        # Title and legends
        plt.title("ReactoN AWR Dynamic Batch Profile", fontsize=12, fontweight="bold", pad=15)
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines1p, labels1p = ax1_p.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines1p + lines2, labels1 + labels1p + labels2, loc="upper left", frameon=True, framealpha=0.9)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_pid_performance(cls, history: List[Dict[str, Any]], save_path: str = None):
        """
        Plot PID setpoint tracking and control valve outputs.
        """
        df = pd.DataFrame(history)
        cls.apply_custom_style()
        fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=300)
        
        time_min = df["time_s"] / 60.0
        
        # Core Temperature vs Setpoint
        ax1.plot(time_min, df["setpoint_c"], color="#888888", linestyle=":", linewidth=1.5, label="Setpoint Temp")
        ax1.plot(time_min, df["temperature_c"], color=cls.danger_color, linewidth=1.8, label="Reactor Core Temp")
        ax1.set_xlabel("Time (minutes)", fontweight="bold")
        ax1.set_ylabel("Temperature (°C)", fontweight="bold")
        ax1.grid(True, **cls.grid_style)
        
        # Coolant Flow Rate on right axis
        ax2 = ax1.twinx()
        color_flow = cls.secondary_color
        ax2.step(time_min, df["coolant_flow_l_min"], color=color_flow, where="post", linewidth=1.5, label="Coolant Flow Rate")
        ax2.set_ylabel("Coolant Flow Rate (L/min)", color=color_flow, fontweight="bold")
        ax2.tick_params(axis="y", labelcolor=color_flow)
        
        plt.title("ReactoN Virtual PLC PID Closed-Loop Response", fontsize=12, fontweight="bold", pad=15)
        
        # Legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", frameon=True, framealpha=0.9)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_polarization_curve(cls, stack_results: List[Dict[str, float]], save_path: str = None):
        """
        Plot fuel cell voltage-current-power characteristics.
        """
        df = pd.DataFrame(stack_results)
        cls.apply_custom_style()
        fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=300)
        
        currents = df["current_amps"]
        
        # Cell Voltage Polarization
        color_v = cls.primary_color
        ax1.plot(currents, df["cell_voltage_v"], color=color_v, linewidth=2.0, label="Cell Voltage (V)")
        ax1.set_xlabel("Stack Current Load (Amps)", fontweight="bold")
        ax1.set_ylabel("Individual Cell Voltage (V)", color=color_v, fontweight="bold")
        ax1.tick_params(axis="y", labelcolor=color_v)
        ax1.set_ylim(0.0, 1.2)
        ax1.grid(True, **cls.grid_style)
        
        # Stack Power Output on right axis
        ax2 = ax1.twinx()
        color_p = cls.accent_color
        ax2.plot(currents, df["power_output_w"], color=color_p, linewidth=2.0, linestyle="--", label="Stack Power (W)")
        ax2.set_ylabel("Stack Electrical Power Output (W)", color=color_p, fontweight="bold")
        ax2.tick_params(axis="y", labelcolor=color_p)
        
        plt.title("PEM Fuel Cell Stack Loading Characteristics", fontsize=12, fontweight="bold", pad=15)
        
        # Legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True, framealpha=0.9)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
