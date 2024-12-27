import streamlit as st
from typing import List, Dict
import math

# ==============================================
# ================ HELPER FUNCTIONS ============
# ==============================================

def calculate_daily_energy_usage(appliances: List[Dict]) -> float:
    """
    Calculate total daily energy usage (Wh) for a list of appliances.
    """
    return sum(appl["wattage"] * appl["hours_per_day"] for appl in appliances)

def calculate_nighttime_energy_usage(appliances: List[Dict]) -> float:
    """
    Calculate the total nighttime energy usage (Wh) for selected appliances.
    """
    return sum(appl["wattage"] * appl["night_hours"] for appl in appliances if appl["use_at_night"])

def calculate_number_of_panels(total_wh: float, panel_wattage: float, sun_hours: float, efficiency: float) -> int:
    """
    Calculate the number of solar panels needed.
    """
    total_wp = total_wh / (sun_hours * efficiency)
    return math.ceil(total_wp / panel_wattage)

def calculate_battery_capacity(total_wh: float, voltage: float, dod: float, efficiency: float) -> float:
    """
    Calculate required battery capacity (Ah).
    """
    return total_wh / (voltage * dod * efficiency)

def calculate_number_of_batteries(total_ah: float, single_battery_ah: float) -> int:
    """
    Calculate the number of batteries needed.
    """
    return math.ceil(total_ah / single_battery_ah)

def calculate_inverter_size(appliances: List[Dict]) -> float:
    """
    Estimate inverter size (W).
    """
    total_wattage = sum(appl["wattage"] for appl in appliances)
    return total_wattage * 1.25

def determine_battery_voltage(system_size: float) -> int:
    """
    Determine appropriate battery bank voltage.
    """
    if system_size <= 1.5:
        return 12
    elif system_size <= 5:
        return 24
    else:
        return 48

# ==============================================
# ================ STREAMLIT APP ==============
# ==============================================

def main():
    st.set_page_config(page_title="Solar Sizing Tool", layout="wide")
    st.title("Smart Solar Sizing Tool")

    st.sidebar.header("System Configuration")

    # Dropdown for selecting solar panel wattages
    panel_wattage = st.sidebar.selectbox("Solar Panel Wattage (W)", [160, 320, 410, 475, 550, 640])
    peak_sun_hours = st.sidebar.number_input("Peak Sun Hours", value=5.0, min_value=1.0, step=0.1)
    system_efficiency = st.sidebar.slider("System Efficiency (%)", 50, 100, 85) / 100

    # Pre-configured packages
    package = st.sidebar.selectbox(
        "Pre-configured Packages",
        ["Custom", "1.5kVA Basic", "1.5kVA Premium", "3kVA Basic", "3kVA Premium", "5kVA"]
    )

    # Battery configuration
    single_battery_ah = st.sidebar.number_input("Single Battery Capacity (Ah)", value=100, min_value=10, step=10)
    battery_type = st.sidebar.selectbox("Battery Type", ["Lead-Acid", "Lithium-Ion"])
    dod = 0.5 if battery_type == "Lead-Acid" else 0.8
    round_trip_efficiency = 0.9 if battery_type == "Lead-Acid" else 0.95

    # Nighttime usage hours
    night_hours = st.sidebar.number_input("Nighttime Usage Hours", value=6, min_value=1, step=1)

    # Appliance inputs
    st.subheader("Appliance Configuration")

    if "appliances" not in st.session_state:
        st.session_state["appliances"] = []

    appliance_name = st.text_input("Appliance Name")
    wattage = st.number_input("Wattage (W)", min_value=1, value=100, step=10)
    hours_per_day = st.number_input("Hours per Day", min_value=0.1, value=1.0, step=0.1)
    use_at_night = st.checkbox("Use at Night", value=False)

    if st.button("Add Appliance"):
        st.session_state["appliances"].append({
            "name": appliance_name,
            "wattage": wattage,
            "hours_per_day": hours_per_day,
            "night_hours": night_hours if use_at_night else 0,
            "use_at_night": use_at_night
        })
        # Clear inputs and refresh
        st.session_state["appliance_name"] = ""
        st.session_state["wattage"] = 0
        st.session_state["hours_per_day"] = 1.0
        st.session_state["use_at_night"] = False
        #st.experimental_set_query_params(refresh=True)  # Use query params to simulate refresh
        st.query_params.from_dict({"refresh": "true"})



    # Display current appliances
    if st.session_state["appliances"]:
        st.write("### Appliance List")
        for idx, appl in enumerate(st.session_state["appliances"]):
            st.write(f"{idx + 1}. {appl['name']} - {appl['wattage']} W, {appl['hours_per_day']} hrs/day, Night: {appl['night_hours']} hrs")
            if st.button(f"Remove {appl['name']}", key=f"remove_{idx}"):
                st.session_state["appliances"].pop(idx)
                #st.experimental_set_query_params(refresh=True)
                st.query_params.from_dict({"refresh": "true"})


    # Perform calculations
    if st.button("Calculate System Requirements"):
        daily_wh = calculate_daily_energy_usage(st.session_state["appliances"])
        nighttime_wh = calculate_nighttime_energy_usage(st.session_state["appliances"])
        system_size_kva = max(wattage for appl in st.session_state["appliances"]) / 1000

        # Battery voltage
        battery_voltage = determine_battery_voltage(system_size_kva)

        # Solar panel calculations
        panels_needed = calculate_number_of_panels(daily_wh, panel_wattage, peak_sun_hours, system_efficiency)

        # Battery calculations
        total_battery_ah = calculate_battery_capacity(nighttime_wh, battery_voltage, dod, round_trip_efficiency)
        num_batteries = calculate_number_of_batteries(total_battery_ah, single_battery_ah)

        # Inverter size
        inverter_size = calculate_inverter_size(st.session_state["appliances"])

        # Results
        st.write("### System Requirements")
        st.metric("Total Daily Energy", f"{daily_wh:.2f} Wh")
        st.metric("Nighttime Energy", f"{nighttime_wh:.2f} Wh")
        st.metric("Battery Voltage", f"{battery_voltage} V")
        st.metric("Number of Solar Panels", f"{panels_needed}")
        st.metric("Number of Batteries", f"{num_batteries}")
        st.metric("Inverter Size", f"{inverter_size:.2f} W")

if __name__ == "__main__":
    main()
