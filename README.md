# Solar PV System Sizing Web Application

## Overview
This web application helps users design and size their solar photovoltaic (PV) system by providing comprehensive calculations for loads, inverters, battery banks, and solar panels. Leveraging Streamlit and AI-powered recommendations, the app offers both standard and technical user experiences.

## Features
- 🤖 AI-Powered Recommendations
  - Contextual NLP-driven personalized system design advice
  - Real-time query understanding and intelligent responses
  - Maintains conversation history for nuanced recommendations
  - Adaptive suggestions based on user's specific solar system requirements

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

### 🤖 AI Recommendation Technology

#### Intelligent Context Management
Our AI recommendation system leverages advanced Natural Language Processing (NLP) techniques to provide personalized solar system design advice. Key technologies include:

- **Contextual Awareness**: 
  - Maintains a rolling conversation history
  - Tracks user inputs across different calculation stages
  - Understands the evolving context of the solar system design

- **Adaptive Recommendation Engine**:
  - Uses OpenAI's GPT models for natural language understanding
  - Generates context-aware recommendations based on:
    1. Current system specifications
    2. User's technical expertise
    3. Specific design constraints
    4. Historical conversation context

- **Dynamic Query Handling**:
  - Interprets complex user queries about solar system design
  - Provides technical explanations and practical recommendations
  - Offers suggestions for optimization and component selection

#### NLP-Driven Personalization
The recommendation system employs sophisticated NLP techniques:
- **Intent Recognition**: Accurately identifies user's underlying questions
- **Contextual Embedding**: Converts user inputs into meaningful vector representations
- **Semantic Analysis**: Understands nuanced technical requirements
- **Knowledge Synthesis**: Combines user inputs with comprehensive solar system design knowledge

#### Example Recommendation Scenarios
1. **Load Assessment**:
   - Analyzes entered loads
   - Suggests energy-efficient alternatives
   - Recommends optimal inverter and battery configurations

2. **Technical Queries**:
   - Explains complex solar system design concepts
   - Provides real-time technical guidance
   - Offers system optimization strategies

3. **Constraint Handling**:
   - Identifies potential design limitations
   - Suggests alternative component selections
   - Provides cost-effective recommendations

#### Privacy and Security
- All AI interactions are processed securely
- User data is not stored beyond the current session
- Recommendations are generated in real-time without persistent data retention

## Prerequisites
- Python 3.8+
- Streamlit
- OpenAI API (optional, for AI recommendations)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tadiwamark/solar-pv-system-sizing-app.git
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

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - tadiwamark@gmail.com

Project Link: [https://github.com/tadiwamark/solar-pv-system-sizing-app](https://github.com/tadiwamark/solar-pv-system-sizing-app)

## Acknowledgments
- Streamlit
- OpenAI
- Solar Energy Research Community
