"""
API endpoints for CalorieAI PWA
Add these functions to your Streamlit app
"""

import streamlit as st
import json
import base64
from openai import OpenAI
from datetime import datetime
import requests

def create_api_endpoints():
    """Add API endpoints to Streamlit app"""
    
    # Check if this is an API request
    query_params = st.experimental_get_query_params()
    
    if 'api' in query_params:
        api_action = query_params.get('api', [None])[0]
        
        if api_action == 'analyze_photo':
            handle_photo_analysis()
        elif api_action == 'get_supabase_config':
            handle_supabase_config()
        elif api_action == 'health':
            handle_health_check()
        
        # Stop normal Streamlit execution for API requests
        st.stop()

def handle_photo_analysis():
    """Handle AI photo analysis requests from PWA"""
    try:
        # Get the request method (would be POST in real implementation)
        # For Streamlit, we'll use query params
        
        if 'image_data' in st.experimental_get_query_params():
            image_data = st.experimental_get_query_params()['image_data'][0]
            
            # Initialize OpenAI client
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
            # Analyze the image
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this food image and provide a detailed nutritional breakdown. You MUST respond with ONLY valid JSON in exactly this format:

{
    "foods": [
        {
            "name": "food item name",
            "portion_size": "estimated portion (e.g., '1 cup', '150g', '1 medium')",
            "calories": 200,
            "protein": 15.5,
            "carbs": 25.0,
            "fat": 8.0,
            "fiber": 3.0,
            "sugar": 5.0,
            "sodium": 150.0,
            "confidence": 85
        }
    ],
    "total_calories": 200,
    "notes": "any additional observations about the meal"
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Parse and return the response
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Return JSON response
            st.json(analysis_result)
            
        else:
            st.json({"error": "No image data provided"})
            
    except Exception as e:
        st.json({"error": str(e)})

def handle_supabase_config():
    """Provide Supabase configuration to PWA"""
    try:
        config = {
            "supabase_url": st.secrets["SUPABASE_URL"],
            "supabase_anon_key": st.secrets["SUPABASE_ANON_KEY"],
            "features": {
                "supabase_enabled": True,
                "ai_analysis_enabled": True
            }
        }
        st.json(config)
    except Exception as e:
        st.json({"error": "Configuration not available"})

def handle_health_check():
    """Simple health check endpoint"""
    st.json({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "CalorieAI API"
    })

# Add this to your main Streamlit app
if __name__ == "__main__":
    create_api_endpoints()
