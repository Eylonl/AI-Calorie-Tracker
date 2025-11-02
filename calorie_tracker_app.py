import streamlit as st
import openai
from PIL import Image
import base64
import io
import json
import os
from datetime import datetime, date
import pandas as pd
import hashlib

# Page configuration optimized for mobile/iPhone
st.set_page_config(
    page_title="🍽️ Calorie Tracker",
    page_icon="🍽️",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed"  # Start collapsed on mobile
)

# iPhone PWA and mobile optimization
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="CalorieAI">
<meta name="theme-color" content="#667eea">
<link rel="manifest" href="./manifest.json">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🍽️%3C/text%3E%3C/svg%3E">

<style>
    /* iPhone and mobile optimizations */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Optimize for iPhone screen sizes */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Make buttons larger for touch */
        .stButton > button {
            height: 3rem;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        /* Optimize camera input */
        .stCamera > div {
            border-radius: 15px;
            border: 2px solid #ff6b6b;
        }
        
        /* Better spacing for mobile */
        .stSelectbox, .stTextInput, .stNumberInput {
            margin-bottom: 1rem;
        }
        
        /* Optimize metrics display */
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 15px;
            color: white;
            margin: 0.5rem 0;
        }
        
        /* Make expanders more touch-friendly */
        .streamlit-expanderHeader {
            font-size: 1.1rem;
            padding: 1rem;
        }
        
        /* Optimize sidebar for mobile */
        .css-1d391kg {
            padding-top: 1rem;
        }
    }
    
    /* iPhone specific optimizations */
    @media (max-width: 414px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        /* Larger touch targets */
        .stButton > button {
            height: 3.5rem;
            width: 100%;
        }
        
        /* Better camera button */
        .stCamera button {
            height: 4rem;
            font-size: 1.2rem;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            border: none;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }
    }
    
    /* PWA-style header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        text-align: center;
    }
    
    /* Improved cards for meal display */
    .meal-card {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'meal_history' not in st.session_state:
    st.session_state.meal_history = []
if 'daily_totals' not in st.session_state:
    st.session_state.daily_totals = {}
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def load_meal_history():
    """Load meal history from JSON file"""
    if os.path.exists('meal_history.json'):
        try:
            with open('meal_history.json', 'r') as f:
                data = json.load(f)
                st.session_state.meal_history = data.get('meals', [])
                st.session_state.daily_totals = data.get('daily_totals', {})
        except Exception as e:
            st.error(f"Error loading meal history: {e}")

def save_meal_history():
    """Save meal history to JSON file"""
    try:
        data = {
            'meals': st.session_state.meal_history,
            'daily_totals': st.session_state.daily_totals
        }
        with open('meal_history.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving meal history: {e}")

def encode_image(image):
    """Convert PIL image to base64 string for OpenAI API"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def analyze_food_with_openai(image, api_key):
    """Analyze food image using OpenAI GPT-4 Vision"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Convert image to base64
        base64_image = encode_image(image)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this food image and provide a detailed breakdown. You MUST respond with ONLY valid JSON in exactly this format, with no additional text before or after:

{
    "foods": [
        {
            "name": "food item name",
            "portion_size": "estimated portion (e.g., '1 cup', '150g', '1 medium')",
            "calories": 200,
            "confidence": 85
        }
    ],
    "total_calories": 200,
    "notes": "any additional observations about the meal"
}

Important: 
- Return ONLY the JSON object, no explanatory text
- Be as accurate as possible with portion sizes and calorie estimates
- Use realistic calorie numbers (integers only)
- Confidence should be 0-100 (integer)
- If you're unsure, indicate lower confidence"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        # Parse the JSON response with better error handling
        response_text = response.choices[0].message.content
        
        if not response_text:
            st.error("Empty response from OpenAI")
            return None
        
        # Try to extract JSON from response
        try:
            # First, try to parse the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from within the text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                # No JSON found, create a fallback response
                st.warning("Could not parse AI response. Using fallback analysis.")
                return {
                    "foods": [
                        {
                            "name": "Unknown food item",
                            "portion_size": "1 serving",
                            "calories": 300,
                            "confidence": 50
                        }
                    ],
                    "total_calories": 300,
                    "notes": f"AI response could not be parsed. Raw response: {response_text[:200]}..."
                }
            
            json_str = response_text[start_idx:end_idx]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as json_error:
                st.error(f"JSON parsing failed: {json_error}")
                st.error(f"Raw response: {response_text}")
                return None
        
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        return None

def add_meal_to_history(meal_data, meal_type):
    """Add confirmed meal to history"""
    today = date.today().isoformat()
    
    meal_entry = {
        'date': today,
        'timestamp': datetime.now().isoformat(),
        'meal_type': meal_type,
        'foods': meal_data['foods'],
        'total_calories': meal_data['total_calories'],
        'notes': meal_data.get('notes', '')
    }
    
    st.session_state.meal_history.append(meal_entry)
    
    # Update daily totals
    if today not in st.session_state.daily_totals:
        st.session_state.daily_totals[today] = 0
    st.session_state.daily_totals[today] += meal_data['total_calories']
    
    save_meal_history()

def main():
    # Load meal history on startup
    load_meal_history()
    
    # iPhone-optimized header
    st.markdown("""
    <div class="app-header">
        <h1 style="margin: 0; font-size: 2rem;">🍽️ AI Calorie Tracker</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">📱 Snap, Analyze, Track</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("Settings")
        
        # Password protection for API key access
        api_key = None
        
        # Try to get API key from secrets first (for deployment)
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            app_password = st.secrets.get("APP_PASSWORD", "calorie123")  # Default password
        except:
            # Local development - no secrets available
            st.warning("⚠️ Running in local mode. API key required.")
            api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
            app_password = "calorie123"  # Default password for local use
        
        # If we have an API key from secrets, show password protection
        if api_key and not st.session_state.authenticated:
            st.subheader("🔐 Enter Password")
            password_input = st.text_input("App Password", type="password", help="Enter the app password to access")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Unlock App", type="primary"):
                    if password_input == app_password:
                        st.session_state.authenticated = True
                        st.success("✅ Access granted!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password")
            
            with col2:
                if st.button("Show Hint"):
                    st.info("💡 Default password: calorie123")
            
            st.stop()  # Stop execution until authenticated
        
        # Show logout option if authenticated
        if st.session_state.authenticated:
            if st.button("🔒 Lock App"):
                st.session_state.authenticated = False
                st.rerun()
        
        if not api_key:
            st.warning("Please enter your OpenAI API key to use the app")
            return
        
        st.header("Daily Summary")
        today = date.today().isoformat()
        today_calories = st.session_state.daily_totals.get(today, 0)
        st.metric("Today's Calories", f"{today_calories:.0f}")
        
        # Daily goal (optional)
        daily_goal = st.number_input("Daily Calorie Goal (optional)", min_value=0, value=2000)
        if daily_goal > 0:
            progress = min(today_calories / daily_goal, 1.0)
            st.progress(progress)
            remaining = max(daily_goal - today_calories, 0)
            st.write(f"Remaining: {remaining:.0f} calories")
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📸 Add Meal", "📊 History"])
    
    with tab1:
        st.markdown("### 🍽️ Add New Meal")
        
        # Meal type selection with better mobile layout
        st.markdown("**Select Meal Type:**")
        meal_type = st.selectbox("", ["Breakfast", "Lunch", "Dinner", "Snack"], label_visibility="collapsed")
        
        # iPhone-optimized camera section
        st.markdown("---")
        st.markdown("### 📸 Capture Your Meal")
        st.markdown("*Tap the camera button below to take a photo*")
        
        # Camera input with better mobile styling
        camera_image = st.camera_input("📷 Take Photo", help="Works best with good lighting")
        
        # File upload as alternative with mobile-friendly text
        st.markdown("**Or choose from your photos:**")
        uploaded_file = st.file_uploader("📁 Select Image", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
        
        # Process image
        image_to_analyze = None
        if camera_image is not None:
            image_to_analyze = Image.open(camera_image)
        elif uploaded_file is not None:
            image_to_analyze = Image.open(uploaded_file)
        
        if image_to_analyze is not None:
            # Mobile-optimized image display
            st.markdown("---")
            st.markdown("### 🖼️ Your Photo")
            st.image(image_to_analyze, caption="📱 Captured meal", use_column_width=True)
            
            # Large, prominent analyze button for mobile
            st.markdown("### 🤖 AI Analysis")
            if st.button("🔍 Analyze My Meal", type="primary", use_container_width=True):
                with st.spinner("🧠 AI is analyzing your meal..."):
                    analysis = analyze_food_with_openai(image_to_analyze, api_key)
                    
                    if analysis:
                        st.session_state.current_analysis = analysis
                        st.session_state.current_meal_type = meal_type
                        st.rerun()
        
        # Display analysis results for confirmation
        if 'current_analysis' in st.session_state:
            st.markdown("---")
            st.markdown("### ✅ Review & Confirm")
            analysis = st.session_state.current_analysis
            
            st.markdown("**🍽️ AI Detected Foods:**")
            
            # Mobile-optimized confirmation form
            with st.form("confirm_meal"):
                total_calories = 0
                confirmed_foods = []
                
                for i, food in enumerate(analysis['foods']):
                    # Mobile-friendly food item display
                    st.markdown(f"#### 🥘 {food['name']}")
                    
                    # Stack inputs vertically for mobile
                    portion = st.text_input("Portion Size", value=food['portion_size'], key=f"portion_{i}")
                    calories = st.number_input("Calories", value=food['calories'], min_value=0, key=f"calories_{i}")
                    confidence = st.slider("AI Confidence %", 0, 100, food['confidence'], key=f"confidence_{i}")
                    
                    confirmed_foods.append({
                        'name': food['name'],
                        'portion_size': portion,
                        'calories': calories,
                        'confidence': confidence
                    })
                    total_calories += calories
                    
                    st.markdown("---")  # Separator between foods
                
                # Notes section
                notes = st.text_area("📝 Additional Notes (optional)", value=analysis.get('notes', ''), height=100)
                
                # Total calories display
                st.markdown(f"### 🔥 Total Calories: **{total_calories}**")
                
                # Mobile-optimized buttons
                if st.form_submit_button("✅ Save This Meal", type="primary", use_container_width=True):
                        confirmed_meal = {
                            'foods': confirmed_foods,
                            'total_calories': total_calories,
                            'notes': notes
                        }
                        add_meal_to_history(confirmed_meal, st.session_state.current_meal_type)
                        st.success(f"Meal saved! Total calories: {total_calories}")
                        del st.session_state.current_analysis
                        del st.session_state.current_meal_type
                        st.rerun()
                
                # Cancel button
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    del st.session_state.current_analysis
                    del st.session_state.current_meal_type
                    st.rerun()
    
    with tab2:
        st.header("Meal History")
        
        if not st.session_state.meal_history:
            st.info("No meals recorded yet. Add your first meal in the 'Add Meal' tab!")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                date_filter = st.date_input("Filter by Date (optional)")
            with col2:
                meal_type_filter = st.selectbox("Filter by Meal Type", ["All", "Breakfast", "Lunch", "Dinner", "Snack"])
            
            # Display meals grouped by day
            filtered_meals = st.session_state.meal_history
            
            if date_filter:
                filtered_meals = [m for m in filtered_meals if m['date'] == date_filter.isoformat()]
            
            if meal_type_filter != "All":
                filtered_meals = [m for m in filtered_meals if m['meal_type'] == meal_type_filter]
            
            # Group meals by date
            from collections import defaultdict
            meals_by_date = defaultdict(list)
            for meal in filtered_meals:
                meals_by_date[meal['date']].append(meal)
            
            # Sort dates in descending order (most recent first)
            sorted_dates = sorted(meals_by_date.keys(), reverse=True)
            
            for date_str in sorted_dates:
                daily_meals = meals_by_date[date_str]
                daily_total = sum(meal['total_calories'] for meal in daily_meals)
                
                # Convert date string to readable format
                date_obj = datetime.fromisoformat(date_str + "T00:00:00").date()
                readable_date = date_obj.strftime("%A, %B %d, %Y")
                
                # Show daily header with total calories
                st.subheader(f"📅 {readable_date}")
                st.metric("Daily Total", f"{daily_total:.0f} calories", delta=None)
                
                # Sort meals within the day by time
                daily_meals.sort(key=lambda x: x['timestamp'])
                
                # Display each meal for this day
                for meal in daily_meals:
                    time_str = meal['timestamp'][11:16]  # Extract HH:MM
                    with st.expander(f"{time_str} - {meal['meal_type']} ({meal['total_calories']:.0f} calories)"):
                        st.write("**Foods:**")
                        for food in meal['foods']:
                            st.write(f"- {food['name']}: {food['portion_size']} ({food['calories']} calories)")
                        if meal['notes']:
                            st.write(f"**Notes:** {meal['notes']}")
                
                st.divider()  # Add separator between days
            
            # Daily summary chart
            if st.session_state.daily_totals:
                st.subheader("Daily Calorie Trends")
                df = pd.DataFrame(list(st.session_state.daily_totals.items()), columns=['Date', 'Calories'])
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                st.line_chart(df.set_index('Date'))

if __name__ == "__main__":
    main()
