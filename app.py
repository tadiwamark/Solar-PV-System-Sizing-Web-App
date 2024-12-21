import streamlit as st
from typing import List, Dict

# -----------------------------
# Helper functions
# -----------------------------

def calculate_daily_energy_usage(appliances: List[Dict]) -> float:
    """
    Calculates total daily energy usage in Wh based on the list of appliances.
    Each appliance dict has: {'name': str, 'wattage': float, 'hours_per_day': float}.
    """
    total_daily_energy = 0.0
    for appliance in appliances:
        total_daily_energy += appliance['wattage'] * appliance['hours_per_day']
    return total_daily_energy

def calculate_nighttime_energy_usage(appliances: List[Dict], night_hours: float) -> float:
    """
    Calculates total nighttime energy usage (Wh).
    For simplicity, assume all appliances run at night for 'night_hours'.
    """
    total_nighttime_energy = 0.0
    for appliance in appliances:
        total_nighttime_energy += appliance['wattage'] * night_hours
    return total_nighttime_energy

def calculate_number_of_panels(total_daily_energy: float, 
                               panel_wattage: float, 
                               peak_sun_hours: float, 
                               system_efficiency: float) -> int:
    """
    Returns the approximate number of panels (integer, rounded up),
    given daily energy in Wh, panel wattage, peak sun hours, and system efficiency (0-1).
    """
    panel_daily_production = panel_wattage * peak_sun_hours * system_efficiency
    if panel_daily_production <= 0:
        return 0  # Avoid division by zero
    raw_panels = total_daily_energy / panel_daily_production
    return int(raw_panels + 0.9999)  # round up

def calculate_battery_capacity(nighttime_energy: float,
                               battery_nominal_voltage: float,
                               depth_of_discharge: float) -> float:
    """
    Returns required battery capacity in Ah to supply 'nighttime_energy' Wh
    (plus a margin for inefficiencies).
    """
    if battery_nominal_voltage <= 0 or depth_of_discharge <= 0:
        return 0.0
    
    required_wh = nighttime_energy * 1.1  # add 10% margin
    battery_ah = required_wh / (battery_nominal_voltage * depth_of_discharge)
    return battery_ah

def calculate_number_of_batteries(required_battery_ah: float,
                                  single_battery_ah: float) -> int:
    """
    Returns the number of batteries (integer, rounded up),
    given total required battery Ah and a single battery's nominal Ah rating.
    """
    if single_battery_ah <= 0:
        return 0
    raw_batteries = required_battery_ah / single_battery_ah
    return int(raw_batteries + 0.9999)  # round up

def calculate_inverter_size(appliances: List[Dict]) -> float:
    """
    Returns recommended inverter size (in W), 
    set to total load wattage + ~20% margin.
    """
    total_wattage = sum(appl['wattage'] for appl in appliances)
    return total_wattage * 1.2  # 20% margin

# -----------------------------
# Main Streamlit App
# -----------------------------

def main():
    # Basic page config
    st.set_page_config(page_title="Solar PV Sizing Tool", layout="wide")

    # Title & Intro
    st.title("Solar PV System Sizing Tool")
    st.markdown("""
    Use this tool to approximate your solar system requirements (panels, batteries, and inverter).
    **Disclaimer**: These are simplified estimates for demonstration. Always consult a professional for precise design.
    """)

    # Sidebar
    st.sidebar.header("System Parameters / Assumptions")

    # 1) Panel Inputs
    panel_wattage = st.sidebar.number_input(
        label="Solar Panel Wattage (W)",
        min_value=10,
        value=300,
        step=10
    )
    peak_sun_hours = st.sidebar.number_input(
        label="Peak Sun Hours (hours/day)",
        min_value=1.0,
        value=5.0,
        step=0.5
    )
    system_efficiency = st.sidebar.slider(
        label="System Efficiency (%)",
        min_value=50,
        max_value=100,
        value=80
    ) / 100.0

    # 2) Battery Inputs
    battery_type = st.sidebar.selectbox("Battery Type", ["Lithium", "Gel"], index=0)
    battery_voltage = st.sidebar.selectbox("Battery Voltage (V)", [12, 24, 48], index=0)
    depth_of_discharge = st.sidebar.slider(
        label="Depth of Discharge (%)",
        min_value=10,
        max_value=100,
        value=50
    ) / 100.0
    single_battery_ah = st.sidebar.number_input(
        label=f"{battery_type} Battery Capacity (Ah)",
        min_value=10,
        value=100,
        step=10
    )

    st.sidebar.markdown("---")
    # 3) Nighttime Usage
    night_hours = st.sidebar.number_input(
        label="Nighttime Usage (hours)",
        min_value=1,
        value=6
    )

    # Initialize session state for appliances if it doesn't exist
    if "appliances" not in st.session_state:
        st.session_state.appliances = []

    # ~~~~~~~~~~~~~ Appliance Input Section ~~~~~~~~~~~~~~
    st.subheader("1. Appliance Details")

    st.markdown("""
    Enter the appliance name, wattage, and daily usage hours.  
    Click 'Add Appliance' to include it in the list.
    """)

    # Temporary keys for new appliance
    if "temp_name" not in st.session_state:
        st.session_state.temp_name = ""
    if "temp_wattage" not in st.session_state:
        st.session_state.temp_wattage = 0
    if "temp_hours" not in st.session_state:
        st.session_state.temp_hours = 1.0

    # Callback to add an appliance
    def add_appliance():
        name = st.session_state.temp_name.strip()
        wattage = st.session_state.temp_wattage
        hours_per_day = st.session_state.temp_hours
        
        # Basic validation
        if not name:
            st.warning("Please enter a valid appliance name.")
            return
        if wattage <= 0:
            st.warning("Wattage must be greater than 0.")
            return
        if hours_per_day < 0:
            st.warning("Hours per day must be 0 or more.")
            return

        st.session_state.appliances.append({
            "name": name,
            "wattage": float(wattage),
            "hours_per_day": float(hours_per_day)
        })

        # Clear temp fields
        st.session_state.temp_name = ""
        st.session_state.temp_wattage = 0
        st.session_state.temp_hours = 1.0

    # Appliance input widgets
    colA, colB, colC = st.columns([2,1.5,1.5])
    with colA:
        st.text_input("Appliance Name", key="temp_name")
    with colB:
        st.number_input("Wattage (W)", min_value=0, value=0, step=10, key="temp_wattage")
    with colC:
        st.number_input("Hours/day", min_value=0.0, value=1.0, step=0.5, key="temp_hours")

    # Add button
    st.button("Add Appliance", on_click=add_appliance)

    # Display existing appliances
    if st.session_state.appliances:
        st.markdown("### Current Appliances")
        for idx, appl in enumerate(st.session_state.appliances):
            c1, c2, c3, c4 = st.columns([3,2,2,1.5])
            with c1:
                st.write(f"**{appl['name']}**")
            with c2:
                st.write(f"{appl['wattage']} W")
            with c3:
                st.write(f"{appl['hours_per_day']} hrs/day")
            with c4:
                if st.button(f"Remove {appl['name']}", key=f"remove_{idx}"):
                    st.session_state.appliances.pop(idx)
                    st.experimental_rerun()

    # ~~~~~~~~~~~~~ Calculation Section ~~~~~~~~~~~~~~
    st.subheader("2. Calculate System Requirements")
    
    if st.button("Calculate"):
        # 1) Daily & nighttime energy usage
        daily_energy_wh = calculate_daily_energy_usage(st.session_state.appliances)
        nighttime_energy_wh = calculate_nighttime_energy_usage(st.session_state.appliances, night_hours)

        # 2) Number of panels
        num_panels = calculate_number_of_panels(
            total_daily_energy=daily_energy_wh,
            panel_wattage=panel_wattage,
            peak_sun_hours=peak_sun_hours,
            system_efficiency=system_efficiency
        )

        # 3) Battery capacity & count
        required_battery_ah = calculate_battery_capacity(
            nighttime_energy=nighttime_energy_wh,
            battery_nominal_voltage=battery_voltage,
            depth_of_discharge=depth_of_discharge
        )
        num_batteries = calculate_number_of_batteries(
            required_battery_ah,
            single_battery_ah
        )

        # 4) Inverter size
        inverter_size_watts = calculate_inverter_size(st.session_state.appliances)

        # ~~~~~~~~~~~~~ Display Results ~~~~~~~~~~~~~
        st.markdown("### Results")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Daily Energy", f"{daily_energy_wh:.2f} Wh")
        with r2:
            st.metric("Nighttime Energy", f"{nighttime_energy_wh:.2f} Wh")
        with r3:
            st.metric("Recommended Inverter Size", f"{inverter_size_watts:.2f} W")

        r4, r5 = st.columns(2)
        with r4:
            st.metric("Number of Solar Panels", num_panels)
        with r5:
            st.metric("Number of Batteries", num_batteries)

        st.info(f"Battery Type Selected: **{battery_type}**")
        st.info("""
        **Note**: These calculations are approximations and assume:
        - No shading or panel mismatch losses beyond the chosen 'System Efficiency'.
        - All appliances might run simultaneously for the hours specified.
        - Only nighttime hours are served by the battery (with a 10% margin).
        - The inverter size includes a 20% buffer for inrush or simultaneous loads.
        """)

if __name__ == "__main__":
    main()
