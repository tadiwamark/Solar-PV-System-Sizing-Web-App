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
    For simplicity, we assume user wants the same subset of appliances at night.
    
    night_hours: The number of hours the user wants to power these appliances at night.
    Returns energy in Wh (watt-hours).
    """
    total_nighttime_energy = 0.0
    for appliance in appliances:
        wattage = appliance['wattage']
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
    panel_daily_production = panel_wattage * peak_sun_hours * system_efficiency
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
    required_wh = nighttime_energy * 1.1  # 10% margin
    if (battery_nominal_voltage * depth_of_discharge) > 0:
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
        return int(batteries_needed + 0.9999)
    else:
        return 0

def calculate_inverter_size(appliances: List[Dict]) -> float:
    """
    Calculates an approximate inverter size in watts.
    This is often sized to the maximum simultaneous load (sum of wattages).
    
    Returns recommended inverter size in watts.
    """
    total_wattage = sum(appl['wattage'] for appl in appliances)
    recommended_inverter_watts = total_wattage * 1.2  # 20% margin
    return recommended_inverter_watts

# =========================================================
# ================ STREAMLIT APP ==========================
# =========================================================

def main():
    # Set page config
    st.set_page_config(page_title="Solar Sizing Tool", layout="wide")
    
    # Title / Intro
    st.title("Solar PV System Sizing Tool")
    st.markdown("""
    This tool helps you estimate how many solar panels, batteries, and the inverter size you need,
    given your daily load requirements and desired nighttime operation.
    
    **Note**: All calculations here are simplified estimates. Always consult with a professional for an accurate design.
    """)

    # Sidebar defaults/assumptions
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

    # Initialize session_state if needed
    if "appliances" not in st.session_state:
        st.session_state.appliances = []

    # -----------------------------------------------------
    # APPLIANCE INPUTS SECTION
    # -----------------------------------------------------
    st.subheader("1. Enter Your Appliances and Usage")

    st.write("Add appliances (name, wattage, and hours per day). Then click 'Add Appliance'.")

    # We'll store the user input in temporary session keys so we can clear them if needed
    if "temp_name" not in st.session_state:
        st.session_state["temp_name"] = ""
    if "temp_wattage" not in st.session_state:
        st.session_state["temp_wattage"] = 0
    if "temp_hours" not in st.session_state:
        st.session_state["temp_hours"] = 1.0

    # Callback for adding an appliance
    def on_add_appliance_click():
        # Only add if name is not empty and wattage is > 0
        name = st.session_state["temp_name"]
        watt = st.session_state["temp_wattage"]
        hrs = st.session_state["temp_hours"]
        
        if name and watt > 0:
            st.session_state.appliances.append({
                'name': name,
                'wattage': float(watt),
                'hours_per_day': float(hrs)
            })
        # Clear the temp input fields (this is allowed since these keys are NOT bound to the widgets)
        st.session_state["temp_name"] = ""
        st.session_state["temp_wattage"] = 0
        st.session_state["temp_hours"] = 1.0
        st.experimental_rerun()  # Force a re-run to refresh the UI

    # Create the input widgets (NOT in a form, so we can easily manage state)
    st.text_input("Appliance Name", key="temp_name")
    st.number_input("Wattage (W)", min_value=0, value=0, step=50, key="temp_wattage")
    st.number_input("Hours per day", min_value=0.0, value=1.0, step=1.0, key="temp_hours")
    
    st.button("Add Appliance", on_click=on_add_appliance_click)

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

    # -----------------------------------------------------
    # CALCULATE SYSTEM REQUIREMENTS
    # -----------------------------------------------------
    st.subheader("2. Calculate System Requirements")

    if st.button("Calculate"):
        # 1) Calculate daily energy usage
        daily_energy = calculate_daily_energy_usage(st.session_state.appliances)  # in Wh

        # 2) Calculate nighttime usage
        nighttime_energy = calculate_nighttime_energy_usage(st.session_state.appliances, night_hours)  # in Wh

        # 3) Calculate number of panels
        num_panels = calculate_number_of_panels(
            total_daily_energy=daily_energy,
            panel_wattage=panel_wattage,
            peak_sun_hours=peak_sun_hours,
            system_efficiency=system_efficiency
        )

        # 4) Calculate battery capacity needed and number of batteries
        battery_capacity_ah = calculate_battery_capacity(
            nighttime_energy=nighttime_energy,
            battery_nominal_voltage=battery_voltage,
            depth_of_discharge=depth_of_discharge
        )
        num_batteries = calculate_number_of_batteries(
            battery_capacity_ah=battery_capacity_ah,
            single_battery_ah=single_battery_ah
        )

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
        **Disclaimer**:
        The above calculations are approximations and assume:
        - All appliances run for the full specified hours (day + night).
        - Ideal conditions with no shading, optimal tilt, etc.
        - 'System Efficiency' to account for inverter and wiring losses.
        - Depth of Discharge (DoD) for batteries so you don’t overly deplete them.
        - Inverter sized to handle total load simultaneously (plus 20% margin).  

        Actual real-world conditions and safe design margins may differ. 
        Always verify with a professional before final purchase or installation.
        """)

if __name__ == "__main__":
    main()
