# AI-Powered Personalized Travel Itinerary Generator

The **AI-Powered Personalized Travel Itinerary Generator** is a Flask-based web application designed to simplify travel planning by generating customized itineraries. With AI integration, the app creates detailed itineraries, visual previews (images and videos), and provides real-time weather updates, offering a seamless and immersive trip-planning experience.

This was our final group project for **ECE:5995 - Generative AI Tools** at the University of Iowa during the Fall 2024 semester.

## Features

- **Personalized Itineraries**: Tailored trip plans based on user preferences like destination, dates, and interests.
- **Visual Previews**: AI-generated images and videos of attractions for better decision-making.
- **Intuitive UI**: A clean, Material Design-inspired interface for easy navigation.
- **Download Itineraries**: Option to download the video and itinerary is available.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or later
- `pip` (Python package manager)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/bmcano/gait-final-project.git
   cd gait-final-project
   ```

2. **Install Dependencies**: Install required Python libraries using the provided `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration Setup**: Create a `.env` file and follow the setup from the `.env.example` file for the API keys

4. **ffmpeg Setup**: In order for `ffmpeg` to work for Python it needs to be installed through import and locally, it can be download here: 
https://ffmpeg.org/download.html 

5. **Demo Mode**: In `config.py` check if `DEMO_MODE` is true or false depending on if you want to use the API keys or not for testing.

6. **Run the Application**: The command below starts the Flask development server on [127.0.0.1:500](http://127.0.0.1:5000)
    ```bash
    python app.py
    ```

### Demo Video

Since GitHub doesn't support video embedding [click here to download the video](https://github.com/bmcano/gait-final-project/blob/main/submission/gait_demo_720p.mp4).
