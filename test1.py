import pytrnsys as pt

# Load TRNSYS model
model = pt.pt.Model("C:\TRNSYS18\Examples\HVACTemplates/mSystem1.dck")

# Set simulation parameters
# model.set_weather_file("path/to/weather.tm2")
model.set_simulation_times(start_time=0, end_time=8760)
model.set_timestep(60)

# Run simulation
model.simulate()

# Retrieve results
outdoor_temp = model.get_variable_values("outdoor_temperature")
room_temp = model.get_variable_values("room_temperature")

# Process results (e.g., plot, save, calculate metrics)
# ...
