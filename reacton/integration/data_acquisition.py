"""
Telemetry acquisition and signal filtering.

Generates synthetic reactor sensor outputs with Gaussian noise and filters 
high-frequency disturbances using Moving Average and Kalman filters.
"""

import numpy as np
from typing import Dict, List

class TelemetryGenerator:
    """
    Simulates physical sensor telemetry outputs for chemical reactors,
    introducing realistic electronic and process noise.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        
    def add_sensor_noise(self, true_value: float, noise_std: float) -> float:
        """
        Add Gaussian white noise to a true sensor measurement.
        """
        noise = self.rng.normal(0.0, noise_std)
        return float(true_value + noise)
        
    def generate_telemetry_batch(
        self,
        true_temperatures: List[float],
        true_pressures: List[float],
        true_flow_rates: List[float],
        temp_noise_std: float = 0.5,
        pressure_noise_std: float = 0.05,
        flow_noise_std: float = 0.1
    ) -> List[Dict[str, float]]:
        """
        Create a timeline of noisy telemetry measurements.
        """
        telemetry = []
        for t, p, f in zip(true_temperatures, true_pressures, true_flow_rates):
            telemetry.append({
                "temperature_measured_c": self.add_sensor_noise(t, temp_noise_std),
                "pressure_measured_bar": self.add_sensor_noise(p, pressure_noise_std),
                "flow_rate_measured_slpm": self.add_sensor_noise(f, flow_noise_std)
            })
        return telemetry

class SignalFilter:
    """
    Signal filtering toolbox for industrial control applications.
    
    Provides:
    - Moving average window filter
    - Single-state linear Kalman filter for dynamic state estimation
    """
    
    def __init__(self):
        # Kalman filter initial states
        self.x_est = 0.0  # Estimated state
        self.P_est = 1.0  # Estimate covariance
        
        # Noise parameters
        self.Q = 0.02     # Process noise covariance
        self.R = 0.5      # Measurement noise covariance
        
    def reset_kalman(self, initial_value: float, estimate_error: float = 1.0):
        """Reset the Kalman filter parameters."""
        self.x_est = initial_value
        self.P_est = estimate_error
        
    def apply_kalman_step(self, measurement: float) -> float:
        """
        Perform a single prediction-correction step of the Kalman Filter.
        
        x_pred = x_est
        P_pred = P_est + Q
        K = P_pred / (P_pred + R)
        x_est = x_pred + K * (measurement - x_pred)
        P_est = (1 - K) * P_pred
        """
        # Prediction
        x_pred = self.x_est
        P_pred = self.P_est + self.Q
        
        # Correction (Kalman Gain)
        K = P_pred / (P_pred + self.R)
        self.x_est = x_pred + K * (measurement - x_pred)
        self.P_est = (1.0 - K) * P_pred
        
        return float(self.x_est)
        
    @staticmethod
    def apply_moving_average(signals: List[float], window_size: int = 5) -> List[float]:
        """
        Apply a moving average smoothing window on a telemetry series.
        """
        if len(signals) == 0:
            return []
            
        smoothed = []
        for i in range(len(signals)):
            start_idx = max(0, i - window_size + 1)
            window = signals[start_idx : i + 1]
            smoothed.append(float(np.mean(window)))
        return smoothed
