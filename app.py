import streamlit as st
from typing import List, Dict

# ==============================================
# ================ HELPER FUNCTIONS ============
# ==============================================

def calculate_daily_energy_usage(appliances: List[Dict]) -> float:
    """
    Calculate total daily energy usage (Wh) for a list of appliances.
    Each appliance is a dict:
      - name (str)
      - wattage (float)
      - hours_per_day (float)
    """
    total_wh = 0.0
    for appl in appliances:
        total_wh += appl["wattage"] * appl["hours_per_day"]
    return total_wh

def calculate_nighttime_energy_usage(appliances: List[Dict], night_hours: float) -> float:
    """
    Calculate the total nighttime energy usage (Wh).
    We assume ALL listed appliances run at night for 'night_hours'.
    If you'd like per-appliance control, you'd store that in the data structure.
    """
    total_wh = 0.0
    for appl in appliances:
        total_wh += appl["wattage"] * night_hours
    return total_wh

def calculate_number_of_panels(daily_energy_wh: float,
                               panel_wattage_w: float,
                               peak_sun_hours: float,
                               system_efficiency: float) -> int:
    """
    Estimate the number of solar panels required to generate 'daily_energy_wh'
    in one day, given:
      - panel_wattage_w: Power rating of one panel (W)
      - peak_sun_hours: Effective sun hours per day
      - system_efficiency: Accounts for losses (0 < system_efficiency <= 1)

    Return the integer number of panels (rounded up).
    """
    # Production from one panel per day:
    panel_daily_wh = panel_wattage_w * peak_sun_hours * system_efficiency
    
    if panel_daily_wh <= 0:
        return 0
    
    # Number of panels:
    raw_count = daily_energy_wh / panel_daily_wh
    return int(raw_count + 0.9999)  # round up

def calculate_battery_capacity_ah(nighttime_wh: float,
                                  battery_nominal_voltage: float,
                                  depth_of_discharge: float,
                                  round_trip_efficiency: float = 0.9) -> float:
    """
    Calculate required battery bank capacity (in Amp-hours) to cover
    the nighttime load 'nighttime_wh', considering:

      - battery_nominal_voltage: e.g., 12, 24, 48 (volts)
      - depth_of_discharge: e.g., 0.5 for Lead-Acid/Gel (50%),
        0.8 for Lithium (80%), etc.
      - round_trip_efficiency: e.g., 0.9 (90%) to account for battery 
        charge/discharge inefficiency.

    Returns the total Ah for the entire bank (at the given nominal voltage).
    """
    if battery_nominal_voltage <= 0 or depth_of_discharge <= 0:
        return 0.0

    # Adjust load for the battery round-trip efficiency
    # (We need MORE energy stored to supply nighttime_wh)
    adjusted_wh = nighttime_wh / round_trip_efficiency

    # Amp-hours needed
    # AH_needed = (Watt-hours) / (Voltage * usable fraction)
    # usable fraction = depth_of_discharge
    if depth_of_discharge > 0:
        ah_needed = adjusted_wh / (battery_nominal_voltage * depth_of_discharge)
    else:
        ah_needed = 0

    return ah_needed

def calculate_number_of_batteries(total_battery_ah: float, single_battery_ah: float) -> int:
    """
    Given the total required battery capacity (Ah) at the chosen nominal voltage,
    and the capacity of one battery (Ah) at the same nominal voltage,
    compute how many batteries are needed in parallel (rounded up).
    
    NOTE: We assume each battery is the same nominal voltage as the bank,
          so we don't do separate series calculations here. 
          If your single battery has a different nominal voltage 
          than the final system, you'd need a more detailed approach.
    """
    if single_battery_ah <= 0:
        return 0
    raw_count = total_battery_ah / single_battery_ah
    return int(raw_count + 0.9999)

def calculate_inverter_size_w(appliances: List[Dict]) -> float:
    """
    Very rough estimate of inverter size (W):
    We assume the worst-case scenario that all appliances can run simultaneously.
    Then add a 20% margin for surge or inefficiencies.
    """
    total_wattage = sum(a["wattage"] for a in appliances)
    return total_wattage * 1.2

# ==============================================
# ================ STREAMLIT APP ==============
# ==============================================

def main():
    st.set_page_config(page_title="Solar Sizing Tool", layout="wide")

    st.title("Solar PV System Sizing Tool")
    st.markdown("""
    This app helps estimate the size of your solar system based on:
    1. Your appliances' wattage and daily usage.
    2. Desired nighttime hours to run them on battery.
    3. Basic panel, battery, and inverter calculations.
    
    > **Disclaimer:** These are **approximate** calculations!
      Always verify with a professional before final purchase or installation.
    """)

    # ---------- SIDEBAR CONFIGURATIONS ----------
    st.sidebar.header("System Defaults / Assumptions")
    # Panels
    panel_wattage = st.sidebar.number_input("Solar Panel Wattage (W)", value=300, min_value=50, step=10)
    peak_sun_hours = st.sidebar.number_input("Peak Sun Hours (hrs)", value=5.0, min_value=1.0, step=0.5)
    system_efficiency = st.sidebar.slider("System Efficiency (%)", 50, 100, 80) / 100.0

    # Battery
    battery_type = st.sidebar.selectbox("Battery Type", ["Lead-Acid/Gel", "Lithium"], index=0)
    if battery_type == "Lead-Acid/Gel":
        # Commonly 50% DoD recommended
        default_dod_percent = 50
    else:
        # Lithium typically can handle 80% DoD
        default_dod_percent = 80

    depth_of_discharge = st.sidebar.slider(
        "Depth of Discharge (%)", 
        min_value=10, 
        max_value=95, 
        value=default_dod_percent
    ) / 100.0

    battery_voltage = st.sidebar.selectbox("Battery Bank Voltage", [12, 24, 48], index=0)
    single_battery_ah = st.sidebar.number_input("Single Battery Capacity (Ah)", value=100, min_value=10, step=10)

    # Battery round trip efficiency (somewhat higher for LiFePO4, typically 90-95%)
    if battery_type == "Lithium":
        round_trip_eff = 0.95
    else:
        round_trip_eff = 0.9

    # Nighttime usage
    night_hours = st.sidebar.number_input("Nighttime Usage Hours", value=6, min_value=1, step=1)

    # ---------- APPLIANCE ENTRIES ----------
    st.subheader("1. Enter Your Appliances and Usage")

    st.write("Add each appliance (name, wattage, daily usage hours) and then press **Add**.")
    st.markdown("""
    **Tip:** If certain appliances won't run at night, you can simply not include them 
    or create two separate lists. This tool currently assumes all listed loads 
    also operate during the night usage hours.
    """)

    # Initialize session state for appliances
    if "appliances" not in st.session_state:
        st.session_state["appliances"] = []

    # We keep temporary inputs in separate keys to avoid the StreamlitAPIException
    if "temp_name" not in st.session_state:
        st.session_state["temp_name"] = ""
    if "temp_wattage" not in st.session_state:
        st.session_state["temp_wattage"] = 0
    if "temp_hours" not in st.session_state:
        st.session_state["temp_hours"] = 1.0

    def add_appliance():
        # Safe-guard: only add if name is non-empty and wattage > 0
        nm = st.session_state["temp_name"].strip()
        wt = st.session_state["temp_wattage"]
        hr = st.session_state["temp_hours"]
        if nm != "" and wt > 0 and hr > 0:
            st.session_state["appliances"].append({
                "name": nm,
                "wattage": float(wt),
                "hours_per_day": float(hr)
            })
        # Reset the fields
        st.session_state["temp_name"] = ""
        st.session_state["temp_wattage"] = 0
        st.session_state["temp_hours"] = 1.0
        st.experimental_rerun()

    # Input widgets (outside a form, using immediate execution)
    st.text_input("Appliance Name", key="temp_name")
    st.number_input("Wattage (W)", min_value=0, value=0, step=50, key="temp_wattage")
    st.number_input("Hours per day", min_value=0.1, value=1.0, step=0.5, key="temp_hours")
    st.button("Add Appliance", on_click=add_appliance)

    # Display the current appliance list
    if st.session_state["appliances"]:
        st.write("### Current Appliance List")
        for i, appl in enumerate(st.session_state["appliances"]):
            c1, c2, c3, c4 = st.columns([3,2,2,1])
            with c1:
                st.write(f"**{appl['name']}**")
            with c2:
                st.write(f"{appl['wattage']} W")
            with c3:
                st.write(f"{appl['hours_per_day']} hrs/day")
            with c4:
                # Remove button
                if st.button(f"Remove {appl['name']}", key=f"remove_{i}"):
                    st.session_state["appliances"].pop(i)
                    st.experimental_rerun()
    else:
        st.info("No appliances added yet!")

    # ---------- CALCULATIONS ----------
    st.subheader("2. Calculate System Requirements")

    if st.button("Calculate Sizing"):
        # 1) Daily energy
        daily_energy_wh = calculate_daily_energy_usage(st.session_state["appliances"])

        # 2) Nighttime load
        nighttime_wh = calculate_nighttime_energy_usage(st.session_state["appliances"], night_hours)

        # 3) Panels needed
        panels_needed = calculate_number_of_panels(
            daily_energy_wh=daily_energy_wh,
            panel_wattage_w=panel_wattage,
            peak_sun_hours=peak_sun_hours,
            system_efficiency=system_efficiency
        )

        # 4) Battery capacity (Ah) needed for nighttime
        battery_capacity_ah = calculate_battery_capacity_ah(
            nighttime_wh,
            battery_nominal_voltage=battery_voltage,
            depth_of_discharge=depth_of_discharge,
            round_trip_efficiency=round_trip_eff
        )

        # 5) Number of batteries
        num_batteries = calculate_number_of_batteries(
            total_battery_ah=battery_capacity_ah,
            single_battery_ah=single_battery_ah
        )

        # 6) Inverter size
        inverter_size = calculate_inverter_size_w(st.session_state["appliances"])

        # ---------- RESULTS ----------
        st.markdown("### Calculation Results")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Daily Energy", f"{daily_energy_wh:.2f} Wh")
        with c2:
            st.metric("Nighttime Energy", f"{nighttime_wh:.2f} Wh")
        with c3:
            st.metric("Inverter (Recommended)", f"{inverter_size:.0f} W")

        c4, c5 = st.columns(2)
        with c4:
            st.metric("Solar Panels Needed", f"{panels_needed}")
        with c5:
            st.metric("Batteries Needed", f"{num_batteries}")

        st.info(f"""
        **Assumptions**:
        - **Battery Type**: {battery_type}  
        - **DoD**: {depth_of_discharge * 100:.0f}%  
        - **Battery Voltage**: {battery_voltage} V  
        - **Round-trip Efficiency**: {round_trip_eff*100:.0f}%  
        - **System Efficiency** (panels): {system_efficiency*100:.0f}%
        
        _Tip: If you find the battery count too high or too low, consider adjusting
        Depth of Discharge, single battery capacity, or nightly load (appliances/hours)._
        """)


if __name__ == "__main__":
    main()
