import streamlit as st
from typing import List, Dict

# =========================================================
# ================ HELPER FUNCTIONS =======================
# =========================================================

def calculate_daily_energy_usage(appliances: List[Dict]) -> float:
    """
    Calculates total daily energy usage based on a list of appliances.
    Each appliance in the list is a dict containing:
      - 'name': str
      - 'wattage': float
      - 'hours_per_day': float
    Returns total daily energy in Wh (watt-hours).
    """
    total_daily_energy = 0.0
    for appliance in appliances:
        wattage = appliance['wattage']
        hours = appliance['hours_per_day']
        total_daily_energy += wattage * hours
    return total_daily_energy

def calculate_nighttime_energy_usage(appliances: List[Dict], night_hours: float) -> float:
    """
    Calculates total nighttime energy usage for the appliances.
    For simplicity, we assume user wants the same subset of appliances at night,
    or they specify the same wattage to use at night for each appliance.
    
    night_hours: The number of hours the user wants to power these appliances at night.
    Returns energy in Wh (watt-hours).
    """
    total_nighttime_energy = 0.0
    for appliance in appliances:
        wattage = appliance['wattage']
        # We assume ALL appliances are running at night if not specifically indicated otherwise.
        # If you'd like to differentiate, add a boolean or separate wattage for nighttime usage.
        total_nighttime_energy += wattage * night_hours
    return total_nighttime_energy

def calculate_number_of_panels(total_daily_energy: float, panel_wattage: float, 
                               peak_sun_hours: float, system_efficiency: float) -> int:
    """
    Calculates the number of solar panels needed given:
      - total_daily_energy (Wh): total watt-hours required per day
      - panel_wattage (W): wattage rating of one solar panel
      - peak_sun_hours (h): average daily peak sun hours in the location
      - system_efficiency: account for inverter/temperature/other losses (range 0-1)
    Returns integer number of panels (rounded up).
    """
    # Energy that can be produced by one panel per day
    panel_daily_production = panel_wattage * peak_sun_hours * system_efficiency
    
    # Number of panels needed
    if panel_daily_production > 0:
        panels_needed = total_daily_energy / panel_daily_production
        return int(panels_needed + 0.9999)  # round up
    else:
        return 0

def calculate_battery_capacity(nighttime_energy: float, battery_nominal_voltage: float,
                               depth_of_discharge: float) -> float:
    """
    Calculates the total battery capacity required in amp-hours.
    nighttime_energy: total watt-hours needed for night usage
    battery_nominal_voltage: voltage of battery (e.g., 12V, 24V)
    depth_of_discharge: fraction of battery capacity that can be used (0-1)
    
    Returns required Amp-hours (Ah).
    """
    # battery capacity in Wh
    # We might add a small safety margin (e.g., 1.1) for inefficiencies if desired.
    required_wh = nighttime_energy * 1.1  # 10% margin
    
    if (battery_nominal_voltage * depth_of_discharge) > 0:
        # convert to amp-hours
        battery_ah = required_wh / (battery_nominal_voltage * depth_of_discharge)
        return battery_ah
    else:
        return 0

def calculate_number_of_batteries(battery_capacity_ah: float, single_battery_ah: float) -> int:
    """
    Calculates the number of batteries needed based on the required amp-hours,
    assuming each battery has a certain nominal amp-hour rating.
    
    Returns integer count of batteries (rounded up).
    """
    if single_battery_ah > 0:
        batteries_needed = battery_capacity_ah / single_battery_ah
        return int(batteries_needed + 0.9999)  # round up
    else:
        return 0

def calculate_inverter_size(appliances: List[Dict]) -> float:
    """
    Calculates an approximate inverter size in watts.
    This is often sized to the maximum simultaneous load.
    For a simpler approach, we sum all wattages (assuming worst-case they're all on).
    A more advanced approach might consider load diversity.
    
    Returns recommended inverter size in watts.
    """
    # Summation of the wattages
    total_wattage = sum(appl['wattage'] for appl in appliances)
    # Add a margin (e.g., 20%) to handle inrush/peak
    recommended_inverter_watts = total_wattage * 1.2
    return recommended_inverter_watts

# =========================================================
# ================ STREAMLIT APP ==========================
# =========================================================

def main():
    st.set_page_config(page_title="Solar Sizing Tool", layout="wide")
    
    # --- Title and Introduction ---
    st.title("Solar PV System Sizing Tool")
    st.markdown("""
    This tool helps you estimate how many solar panels, batteries, and the inverter size you need,
    given your daily load requirements and desired nighttime operation.  
    Please note: **All calculations here are simplified estimates** and are for demonstration purposes. 
    Always consult with a professional for an accurate design.
    """)

    # --- Side Panel / Input Section ---
    st.sidebar.header("System Defaults / Assumptions")
    panel_wattage = st.sidebar.number_input("Solar Panel Wattage (W)", value=300, min_value=50, step=10)
    peak_sun_hours = st.sidebar.number_input("Peak Sun Hours (hrs)", value=5.0, min_value=1.0, step=0.5)
    system_efficiency = st.sidebar.slider("System Efficiency (%)", 50, 100, 80) / 100.0
    
    battery_voltage = st.sidebar.selectbox("Battery Nominal Voltage (V)", [12, 24, 48], index=0)
    depth_of_discharge = st.sidebar.slider("Depth of Discharge (%)", 10, 100, 50) / 100.0
    single_battery_ah = st.sidebar.number_input("Single Battery Capacity (Ah)", value=100, min_value=10, step=10)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Nighttime Operation**")
    night_hours = st.sidebar.number_input("Nighttime Usage Hours", value=6, min_value=1, step=1)

    # --- Appliance Input ---
    st.subheader("1. Enter Your Appliances and Usage")
    st.write("Add the appliances you want to power. For each appliance, provide its wattage (W) and hours used per day.")
    
    # We will store appliances in session_state so that user input persists
    if "appliances" not in st.session_state:
        st.session_state.appliances = []

    appliance_placeholder = st.empty()

    def add_appliance():
        if st.session_state.new_appliance_name and st.session_state.new_appliance_wattage > 0:
            st.session_state.appliances.append({
                'name': st.session_state.new_appliance_name,
                'wattage': float(st.session_state.new_appliance_wattage),
                'hours_per_day': float(st.session_state.new_appliance_hours)
            })
            st.session_state.new_appliance_name = ""
            st.session_state.new_appliance_wattage = 0
            st.session_state.new_appliance_hours = 0

    with st.form("add_appliance_form"):
        st.text_input("Appliance Name", key="new_appliance_name")
        st.number_input("Wattage (W)", min_value=0, value=0, step=50, key="new_appliance_wattage")
        st.number_input("Hours per day", min_value=0.0, value=1.0, step=1.0, key="new_appliance_hours")
        submitted = st.form_submit_button("Add Appliance")
        if submitted:
            add_appliance()

    # Display existing appliances in a table
    if st.session_state.appliances:
        st.write("### Current Appliances")
        for idx, appl in enumerate(st.session_state.appliances):
            col1, col2, col3, col4 = st.columns([3,2,2,1])
            with col1:
                st.write(f"**{appl['name']}**")
            with col2:
                st.write(f"{appl['wattage']} W")
            with col3:
                st.write(f"{appl['hours_per_day']} hrs/day")
            with col4:
                # Remove button
                if st.button(f"Remove {appl['name']}", key=f"remove_{idx}"):
                    st.session_state.appliances.pop(idx)
                    st.experimental_rerun()

    # --- Calculation Button ---
    st.subheader("2. Calculate System Requirements")
    if st.button("Calculate"):
        # 1) Calculate daily energy usage
        daily_energy = calculate_daily_energy_usage(st.session_state.appliances)  # in Wh

        # 2) Calculate nighttime usage
        nighttime_energy = calculate_nighttime_energy_usage(st.session_state.appliances, night_hours)  # in Wh

        # 3) Calculate number of panels
        num_panels = calculate_number_of_panels(daily_energy, panel_wattage, peak_sun_hours, system_efficiency)

        # 4) Calculate battery capacity needed and number of batteries
        battery_capacity_ah = calculate_battery_capacity(nighttime_energy, battery_voltage, depth_of_discharge)
        num_batteries = calculate_number_of_batteries(battery_capacity_ah, single_battery_ah)

        # 5) Inverter size
        inverter_size_watts = calculate_inverter_size(st.session_state.appliances)

        # --- Display the results ---
        st.markdown("### Results")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Daily Energy", value=f"{daily_energy:.2f} Wh")
        with col2:
            st.metric(label="Nighttime Energy", value=f"{nighttime_energy:.2f} Wh")
        with col3:
            st.metric(label="Inverter Size (recommended)", value=f"{inverter_size_watts:.2f} W")

        col4, col5 = st.columns(2)
        with col4:
            st.metric(label="Number of Solar Panels", value=num_panels)
        with col5:
            st.metric(label="Number of Batteries", value=num_batteries)

        # Additional notes / disclaimers
        st.info("""
        **Disclaimer**: The above calculations are approximations and assume:
        - All appliances run for the full specified hours (day + night).  
        - Ideal system conditions (no shading, optimal tilt, etc.)  
        - System efficiency setting accounts for losses in wiring, controller, and inversion.  
        - Depth of discharge (DoD) ensures you don't overly deplete the battery.  
        - Inverter is sized to handle the total load (plus margin).  
        
        Real-world conditions, inefficiencies, and safe design margins will affect actual requirements.
        """)

if __name__ == "__main__":
    main()
