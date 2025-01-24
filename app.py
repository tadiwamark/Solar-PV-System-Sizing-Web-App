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

    # Landing Page
    st.header("Select User Mode")
    user_mode = st.radio("Choose your mode:", ("Non-Technical User", "Technical User"))

    if user_mode == "Technical User":
        st.warning("Coming soon...")
        st.stop()

    # Non-Technical User Section
    st.subheader("Load Input")
    if "loads" not in st.session_state:
        st.session_state["loads"] = []

    load_name = st.text_input("Load Name")
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    wattage = st.number_input("Wattage (W)", min_value=1, value=100, step=10)
    day_hours = st.number_input("Day Hours", min_value=0.0, value=1.0, step=0.1)
    night_hours = st.number_input("Night Hours", min_value=0.0, value=1.0, step=0.1)
    peak_power_surge = st.checkbox("Peak Power Surge")

    if st.button("Add Load"):
        peak_power = wattage * quantity
        peak_power_surge_value = peak_power * 3 if peak_power_surge else peak_power
        day_energy_demand = wattage * quantity * day_hours
        night_energy_demand = wattage * quantity * night_hours
        st.session_state["loads"].append({
            "name": load_name,
            "quantity": quantity,
            "wattage": wattage,
            "day_hours": day_hours,
            "night_hours": night_hours,
            "peak_power": peak_power,
            "peak_power_surge": peak_power_surge_value,
            "day_energy_demand": day_energy_demand,
            "night_energy_demand": night_energy_demand
        })

    # Display Load Table
    if st.session_state["loads"]:
        st.write("### Load Table")
        st.table(st.session_state["loads"])

        # Calculate Totals
        total_peak_power = sum(load["peak_power"] for load in st.session_state["loads"])
        total_peak_power_surge = sum(load["peak_power_surge"] for load in st.session_state["loads"])
        total_day_energy_demand = sum(load["day_energy_demand"] for load in st.session_state["loads"])
        total_night_energy_demand = sum(load["night_energy_demand"] for load in st.session_state["loads"])

        st.metric("Total Peak Power", f"{total_peak_power} W")
        st.metric("Total Peak Power Surge", f"{total_peak_power_surge} W")
        st.metric("Total Day Energy Demand", f"{total_day_energy_demand} Wh")
        st.metric("Total Night Energy Demand", f"{total_night_energy_demand} Wh")

        if st.button("Proceed to Inverter Size Calculations"):
            # Inverter Size Calculation
            inverter_size = total_peak_power * 1.2
            inverter_size_rounded = round(inverter_size / 0.5) * 0.5

            # Determine System Voltage
            if 1000 <= inverter_size_rounded <= 1500:
                system_voltage = 12
            elif 1500 < inverter_size_rounded <= 3000:
                system_voltage = 24
            elif 3000 < inverter_size_rounded <= 5000:
                system_voltage = 48
            else:
                system_voltage = 48

            st.write("### Inverter Size and System Voltage")
            st.metric("Inverter Size", f"{inverter_size_rounded} kVA")
            st.metric("System Voltage", f"{system_voltage} V")

            if st.button("Proceed to Battery Bank Calculations"):
                # Battery Bank Calculations
                st.write("### Battery Bank Calculations")
                battery_options = [
                    (12, 75), (12, 100), (12, 200),
                    (24, 75), (24, 100), (24, 200),
                    (48, 75), (48, 100), (48, 200)
                ]
                available_batteries = [(v, ah) for v, ah in battery_options if v == system_voltage]
                selected_battery = st.selectbox("Select Battery Size", available_batteries)
                battery_bank_size = total_night_energy_demand / system_voltage
                num_batteries = math.ceil(battery_bank_size / selected_battery[1])

                st.metric("Battery Bank Size", f"{battery_bank_size:.2f} Ah")
                st.metric("Number of Batteries", f"{num_batteries}")

                if st.button("Proceed to Solar Panel Calculations"):
                    # Solar Panel Calculations
                    st.write("### Solar Panel Calculations")
                    peak_sun_hours = st.number_input("Peak Sun Hours", min_value=1.0, value=5.0, step=0.1)
                    selected_panel_size = st.selectbox("Select Panel Size", [160, 320, 410, 475, 490, 550, 640])
                    total_required_wattage = total_day_energy_demand / (peak_sun_hours * 0.8 * 0.8)
                    num_panels = math.ceil(total_required_wattage / selected_panel_size)

                    st.metric("Total Required Wattage", f"{total_required_wattage:.2f} W")
                    st.metric("Number of Panels", f"{num_panels}")

                    if st.button("Proceed to Final Summary"):
                        # Final Summary
                        st.write("### Final System Summary")
                        st.write(f"We need: {num_batteries} * {selected_battery[1]}Ah batteries ({system_voltage}V)")
                        st.write(f"1 * {inverter_size_rounded} kVA inverter")
                        st.write(f"{num_panels} * {selected_panel_size}W solar panels")

if __name__ == "__main__":
    main()
