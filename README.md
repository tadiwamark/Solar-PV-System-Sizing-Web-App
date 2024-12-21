# Solar-PV-System-Sizing-Web-App

A simple Streamlit web application to help you approximate your solar system sizing requirements.  

### Features
- **Appliance Input**: Specify appliance name, wattage, and daily usage hours.  
- **Nighttime Usage**: Define how many hours you want the system to run at night.  
- **Sizing Output**: Gives you approximate estimates for:
  - Daily energy usage
  - Number of solar panels required
  - Battery capacity requirements
  - Number of batteries needed
  - Recommended inverter size

## Assumptions
- The system is sized assuming all appliances might run simultaneously for their stated hours.  
- Batteries are sized only for the nighttime hours (plus a small 10% margin).  
- A default panel wattage of 300W and 5 peak sun hours are assumed.  
- System efficiency and depth of discharge can be adjusted in the sidebar.  
- Calculations are simplified and do not account for all real-world losses or design complexities.

## Installation

1. **Clone this repository** or download the project files:
    ```bash
    git clone https://github.com/yourusername/solar-sizing-tool.git
    ```
2. **Navigate to the project directory**:
    ```bash
    cd solar-sizing-tool
    ```
3. **Install the requirements**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```
2. **Open your browser** at the URL typically shown in the terminal (e.g., `http://localhost:8501`).

## Deployment
- **Streamlit Cloud**: Push this repository to GitHub (or similar) and connect it to your Streamlit Cloud account.  
- **Other Platforms**: If using Docker, Heroku, or other hosting services, ensure the environment includes the dependencies listed in `requirements.txt`.

## Contributing
Feel free to open issues or pull requests to improve the code, the UI, or the underlying assumptions and formulas.

## License
This project is licensed under the [MIT License](LICENSE).
