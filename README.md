# Solar PV System Sizing Web Application

## Overview
This web application helps users design and size their solar photovoltaic (PV) system by providing comprehensive calculations for loads, inverters, battery banks, and solar panels. Leveraging Streamlit and AI-powered recommendations, the app offers both standard and technical user experiences.

## Features
- 🔋 Load Input Management
  - Add multiple electrical loads with detailed specifications
  - Calculate total energy demands (day and night)
  - Track peak power and power surge requirements

- 🔌 Inverter Sizing Calculations
  - Automatically determine inverter size based on total load
  - Recommend appropriate system voltage

- 🔋 Battery Bank Sizing
  - Calculate battery bank requirements
  - Determine number and configuration of batteries
  - Support for different battery technologies

- ☀️ Solar Panel Calculations
  - Estimate total solar panel wattage needed
  - Recommend number and configuration of panels
  - Consider peak sun hours and system efficiency

- 📊 Comprehensive System Summary
  - Detailed breakdown of system components
  - Visualization of system configuration

## Prerequisites
- Python 3.8+
- Streamlit
- OpenAI API (optional, for AI recommendations)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/solar-pv-system-sizing-app.git
cd solar-pv-system-sizing-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up OpenAI API Key (Optional):
- Create a `.env` file in the project root
- Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Running the Application
```bash
streamlit run app.py
```

## User Guide
1. **Load Input Page**
   - Enter details for each electrical load
   - Specify quantity, wattage, operational hours
   - Add loads to calculate total energy demand

2. **Inverter Calculations**
   - Automatically calculates inverter size
   - Recommends system voltage based on total load

3. **Battery Bank Sizing**
   - Select battery specifications
   - View recommended battery configuration

4. **Solar Panel Calculations**
   - Input peak sun hours
   - Select panel wattage
   - Calculate total panel requirements

5. **Final Summary**
   - Comprehensive system design overview
   - Detailed component specifications

## Customization
- Modify default specifications in the sidebar
- Adjust calculation parameters as needed

## Technical Details
- Built with Streamlit
- AI-powered recommendations using OpenAI
- Supports multiple battery and panel configurations
- Considers system efficiency and technical constraints

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - tadiwamark@gmail.com

Project Link: [https://github.com/tadiwamark/solar-pv-system-sizing-app](https://github.com/tadiwamark/solar-pv-system-sizing-app)

## Acknowledgments
- Streamlit
- OpenAI
- Solar Energy Research Community
