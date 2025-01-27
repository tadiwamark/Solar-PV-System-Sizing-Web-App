import streamlit as st
from typing import List, Dict
import math
from openai import OpenAI

# Initialize OpenAI client with API key
client = None


def set_openai_api_key(api_key: str):
    global client
    client = OpenAI(api_key=api_key)


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

def get_recommendations(user_inputs: str, goals: str) -> str:
    # Use OpenAI API to get personalized recommendations
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Based on these inputs: {user_inputs} and goals: {goals}, provide a personalized solar system sizing recommendation."}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def answer_query(query: str) -> str:
    # Use OpenAI API to answer user queries
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Answer this query: {query}"}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ==============================================
# ================ STREAMLIT APP ==============
# ==============================================

def load_page():
    st.subheader("Load Input")
    if "loads" not in st.session_state:
        st.session_state["loads"] = []

    load_name = st.text_input("Load Name")
    quantity = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
    wattage = st.number_input("Wattage (W)", min_value=1.0, value=100.0, step=1.0)
    day_hours = st.number_input("Day Hours", min_value=0.0, value=1.0, step=1.0)
    night_hours = st.number_input("Night Hours", min_value=0.0, value=1.0, step=1.0)
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
            st.session_state["page"] = "inverter"


def inverter_page():
    # Inverter Size Calculation
    total_peak_power = sum(load["peak_power"] for load in st.session_state["loads"])
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
        st.session_state["system_voltage"] = system_voltage
        st.session_state["page"] = "battery"


def battery_page():
    # Battery Bank Calculations
    st.write("### Battery Bank Calculations")
    system_voltage = st.session_state.get("system_voltage", 12)
    total_night_energy_demand = sum(load["night_energy_demand"] for load in st.session_state["loads"])

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
        st.session_state["page"] = "solar"


def solar_page():
    # Solar Panel Calculations
    st.write("### Solar Panel Calculations")
    total_day_energy_demand = sum(load["day_energy_demand"] for load in st.session_state["loads"])
    peak_sun_hours = st.number_input("Peak Sun Hours", min_value=1.0, value=5.0, step=0.1)
    selected_panel_size = st.selectbox("Select Panel Size", [160, 320, 410, 475, 490, 550, 640])
    total_required_wattage = total_day_energy_demand / (peak_sun_hours * 0.8 * 0.8)
    num_panels = math.ceil(total_required_wattage / selected_panel_size)

    st.metric("Total Required Wattage", f"{total_required_wattage:.2f} W")
    st.metric("Number of Panels", f"{num_panels}")

    if st.button("Proceed to Final Summary"):
        st.session_state["page"] = "summary"


def summary_page():
    # Final Summary
    st.write("### Final System Summary")
    system_voltage = st.session_state.get("system_voltage", 12)
    total_night_energy_demand = sum(load["night_energy_demand"] for load in st.session_state["loads"])
    battery_options = [
        (12, 75), (12, 100), (12, 200),
        (24, 75), (24, 100), (24, 200),
        (48, 75), (48, 100), (48, 200)
    ]
    available_batteries = [(v, ah) for v, ah in battery_options if v == system_voltage]
    selected_battery = st.selectbox("Select Battery Size", available_batteries)
    battery_bank_size = total_night_energy_demand / system_voltage
    num_batteries = math.ceil(battery_bank_size / selected_battery[1])

    total_day_energy_demand = sum(load["day_energy_demand"] for load in st.session_state["loads"])
    peak_sun_hours = st.number_input("Peak Sun Hours", min_value=1.0, value=5.0, step=0.1)
    selected_panel_size = st.selectbox("Select Panel Size", [160, 320, 410, 475, 490, 550, 640])
    total_required_wattage = total_day_energy_demand / (peak_sun_hours * 0.8 * 0.8)
    num_panels = math.ceil(total_required_wattage / selected_panel_size)

    st.write(f"We need: {num_batteries} * {selected_battery[1]}Ah batteries ({system_voltage}V)")
    st.write(f"1 * {round(sum(load['peak_power'] for load in st.session_state['loads']) * 1.2 / 0.5) * 0.5} kVA inverter")
    st.write(f"{num_panels} * {selected_panel_size}W solar panels")


def technical_user_page():
    st.title("Technical User Solar Sizing Tool")

    # Set initial page to 'load' if not set
    if 'page' not in st.session_state:
        st.session_state['page'] = 'load'

    # Default specifications
    default_battery_dod = {"Lithium": 0.8, "Gel": 0.5}
    default_panel_imp = 11.0  # Current at max power (A)
    default_panel_voc = 53.3  # Open Circuit Voltage (V)
    default_inverter_vmax = 430.0  # Max MPPT Voltage (V)
    default_inverter_vmin = 120.0  # Min MPPT Voltage (V)
    default_inverter_ic = 100.0  # Inverter Current (A)

    # User input for custom specifications
    st.sidebar.header("Custom Specifications")
    battery_dod = st.sidebar.number_input("Battery Depth of Discharge (DoD)", min_value=0.1, max_value=1.0, value=default_battery_dod["Lithium"], step=0.1)
    panel_imp = st.sidebar.number_input("Panel Current at Max Power (Imp)", min_value=1.0, value=default_panel_imp, step=1.0)
    panel_voc = st.sidebar.number_input("Panel Open Circuit Voltage (Voc)", min_value=1.0, value=default_panel_voc, step=1.0)
    inverter_vmax = st.sidebar.number_input("Inverter Max MPPT Voltage (Vmax)", min_value=1.0, value=default_inverter_vmax, step=1.0)
    inverter_vmin = st.sidebar.number_input("Inverter Min MPPT Voltage (Vmin)", min_value=1.0, value=default_inverter_vmin, step=1.0)
    inverter_ic = st.sidebar.number_input("Inverter Current (Ic)", min_value=1.0, value=default_inverter_ic, step=1.0)

    # Page Navigation based on session state
    current_page = st.session_state.get('page', 'load')

    if current_page == 'load':
        # Load input and calculations
        st.subheader("Load Input")
        if "loads" not in st.session_state:
            st.session_state["loads"] = []

        load_name = st.text_input("Load Name")
        quantity = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
        wattage = st.number_input("Wattage (W)", min_value=1.0, value=100.0, step=1.0)
        day_hours = st.number_input("Day Hours", min_value=0.0, value=1.0, step=1.0)
        night_hours = st.number_input("Night Hours", min_value=0.0, value=1.0, step=1.0)
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
                st.session_state["page"] = "inverter"
                st.rerun()

    elif current_page == "inverter":
        # Inverter Size Calculation
        total_peak_power = sum(load["peak_power"] for load in st.session_state["loads"])
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

        # Store calculations in session state
        st.session_state["inverter_size_rounded"] = inverter_size_rounded

        st.write("### Inverter Size and System Voltage")
        st.metric("Inverter Size", f"{inverter_size_rounded} kVA")
        st.metric("System Voltage", f"{system_voltage} V")

        if st.button("Proceed to Battery Bank Calculations"):
            st.session_state["system_voltage"] = system_voltage
            st.session_state["page"] = "battery"
            st.rerun()

    elif current_page == "battery":
        total_night_energy_demand = sum(load["night_energy_demand"] for load in st.session_state["loads"])
        system_voltage = st.session_state.get("system_voltage", 12)

        st.write("### Technical Battery Bank Calculations")
        battery_options = [
            (12, 75), (12, 100), (12, 200),
            (24, 75), (24, 100), (24, 200),
            (48, 75), (48, 100), (48, 200)
        ]
        available_batteries = [(v, ah) for v, ah in battery_options if v == system_voltage]
        selected_battery = st.selectbox("Select Battery Size", available_batteries)
        battery_bank_size = total_night_energy_demand / system_voltage
        num_batteries = math.ceil(battery_bank_size / selected_battery[1])

        # Calculate max batteries in parallel and series
        max_batteries_parallel = total_night_energy_demand / (selected_battery[1] * battery_dod)
        max_batteries_series = system_voltage / selected_battery[0]

        # Store calculations in session state
        st.session_state["selected_battery"] = selected_battery
        st.session_state["num_batteries"] = num_batteries
        st.session_state["max_batteries_parallel"] = max_batteries_parallel
        st.session_state["max_batteries_series"] = max_batteries_series

        st.metric("Battery Bank Size", f"{battery_bank_size:.2f} Ah")
        st.metric("Number of Batteries", f"{num_batteries}")
        st.metric("Max Batteries in Parallel", f"{max_batteries_parallel:.0f}")
        st.metric("Max Batteries in Series", f"{max_batteries_series:.0f}")

        if st.button("Proceed to Solar Panel Calculations"):
            st.session_state["page"] = "solar"
            st.rerun()

    elif current_page == "solar":
        total_day_energy_demand = sum(load["day_energy_demand"] for load in st.session_state["loads"])

        st.write("### Technical Solar Panel Calculations")
        peak_sun_hours = st.number_input("Peak Sun Hours", min_value=1.0, value=5.0, step=0.1)
        selected_panel_size = st.selectbox("Select Panel Size", [160, 320, 410, 475, 490, 550, 640])
        total_required_wattage = total_day_energy_demand / (peak_sun_hours * 0.8 * 0.8)
        num_panels = math.ceil(total_required_wattage / selected_panel_size)

        # Calculate max panels in parallel and series
        max_panels_parallel = inverter_ic / panel_imp
        max_panels_series_vmax = inverter_vmax / panel_voc
        max_panels_series_vmin = inverter_vmin / panel_voc

        # Store calculations in session state
        st.session_state["selected_panel_size"] = selected_panel_size
        st.session_state["num_panels"] = num_panels
        st.session_state["max_panels_parallel"] = max_panels_parallel
        st.session_state["max_panels_series_vmax"] = max_panels_series_vmax
        st.session_state["max_panels_series_vmin"] = max_panels_series_vmin

        st.metric("Total Required Wattage", f"{total_required_wattage:.2f} W")
        st.metric("Number of Panels", f"{num_panels}")
        st.metric("Max Panels in Parallel", f"{max_panels_parallel:.0f}")
        st.metric("Max Panels in Series (Vmax)", f"{max_panels_series_vmax:.0f}")
        st.metric("Max Panels in Series (Vmin)", f"{max_panels_series_vmin:.0f}")

        if st.button("Proceed to Final Summary"):
            st.session_state["page"] = "summary"
            st.rerun()

    elif current_page == "summary":
        st.write("### Final Technical System Summary")
        
        # Retrieve values from session state
        selected_battery = st.session_state.get("selected_battery")
        num_batteries = st.session_state.get("num_batteries")
        system_voltage = st.session_state.get("system_voltage")
        selected_panel_size = st.session_state.get("selected_panel_size")
        num_panels = st.session_state.get("num_panels")
        max_batteries_parallel = st.session_state.get("max_batteries_parallel")
        max_batteries_series = st.session_state.get("max_batteries_series")
        max_panels_parallel = st.session_state.get("max_panels_parallel")
        max_panels_series_vmax = st.session_state.get("max_panels_series_vmax")
        max_panels_series_vmin = st.session_state.get("max_panels_series_vmin")
        inverter_size_rounded = st.session_state.get("inverter_size_rounded")

        st.write(f"We need: {num_batteries} * {selected_battery[1]}Ah batteries ({system_voltage}V)")
        st.write(f"1 * {inverter_size_rounded} kVA inverter")
        st.write(f"{num_panels} * {selected_panel_size}W solar panels")
        st.write(f"Max Batteries in Parallel: {max_batteries_parallel:.0f}")
        st.write(f"Max Batteries in Series: {max_batteries_series:.0f}")
        st.write(f"Max Panels in Parallel: {max_panels_parallel:.0f}")
        st.write(f"Max Panels in Series (Vmax): {max_panels_series_vmax:.0f}")
        st.write(f"Max Panels in Series (Vmin): {max_panels_series_vmin:.0f}")


def ai_powered_solar_assistant_page():
    # Initialize conversation history in session state if not exists
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Sidebar for conversation management
    with st.sidebar:
        st.header("Conversation Management")
        
        # View Conversation History
        if st.button("View Conversation History"):
            st.write("### Conversation History")
            for idx, message in enumerate(st.session_state.conversation_history, 1):
                role = "👤 User" if message['role'] == 'user' else "🤖 AI"
                st.text(f"{role}: {message['content']}")
        
        # Clear Conversation History
        if st.button("Clear Conversation History"):
            st.session_state.conversation_history = []
            st.success("Conversation history has been cleared.")

    st.title("AI Powered Solar Assistant")

    # Input for OpenAI API Key
    openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if openai_api_key:
        set_openai_api_key(openai_api_key)

        # User inputs and goals
        user_inputs = st.text_area("Enter your system requirements and preferences:")
        goals = st.text_input("Set your goals (e.g., going 100% off-grid):")

        if st.button("Get AI Recommendations"):
            if user_inputs and goals:
                # Prepare messages with system context
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Based on these inputs: {user_inputs} and goals: {goals}, provide a personalized solar system sizing recommendation."}
                ]
                
                # Add previous conversation context
                messages.extend(st.session_state.conversation_history)
                
                # Add current user input
                current_user_message = {
                    "role": "user", 
                    "content": f"System Requirements: {user_inputs}\nGoals: {goals}\n\nProvide a comprehensive, personalized solar system sizing recommendation."
                }
                messages.append(current_user_message)

                # Get recommendation
                try:
                    completion = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages
                    )
                    recommendations = completion.choices[0].message.content.strip()
                    
                    # Display recommendations
                    st.write("### Personalized Recommendations")
                    st.write(recommendations)
                    
                    # Store the recommendation and user input in conversation history
                    st.session_state.conversation_history.extend([
                        current_user_message,
                        {"role": "assistant", "content": recommendations}
                    ])
                
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
            else:
                st.warning("Please provide both system requirements and goals.")

        # Follow-up Questions Section
        st.write("### Ask a Question About Your Recommendation")
        query = st.text_input("Enter your follow-up question:")
        if st.button("Ask AI"):
            if query and st.session_state.conversation_history:
                # Prepare messages with full conversation context
                messages = [
                    {"role": "system", "content": "You are an expert solar system design assistant. Provide detailed, contextual answers based on the previous conversation about solar system design."}
                ]
                
                # Add previous conversation context
                messages.extend(st.session_state.conversation_history)
                
                # Add current query
                current_query_message = {"role": "user", "content": query}
                messages.append(current_query_message)

                # Get answer
                try:
                    completion = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages
                    )
                    answer = completion.choices[0].message.content.strip()
                    
                    # Display answer
                    st.write("### Answer")
                    st.write(answer)
                    
                    # Store the query and answer in conversation history
                    st.session_state.conversation_history.extend([
                        current_query_message,
                        {"role": "assistant", "content": answer}
                    ])
                
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
            else:
                st.warning("Please enter a question and ensure you have a previous recommendation.")
    else:
        st.warning("Please enter your OpenAI API Key to use the AI features.")


def main():
    st.set_page_config(page_title="Solar Sizing Tool", layout="wide")
    st.title("Smart Solar Sizing Tool")

    # Landing Page
    st.header("Select User Mode")
    user_mode = st.radio("Choose your mode:", ("Non-Technical User", "Technical User", "AI Powered Solar Assistant"))

    if user_mode == "Technical User":
        technical_user_page()
        st.stop()
    elif user_mode == "AI Powered Solar Assistant":
        ai_powered_solar_assistant_page()
        st.stop()

    # Page Navigation
    page = st.session_state.get("page", "load")

    if page == "load":
        load_page()
    elif page == "inverter":
        inverter_page()
    elif page == "battery":
        battery_page()
    elif page == "solar":
        solar_page()
    elif page == "summary":
        summary_page()


if __name__ == "__main__":
    main()
