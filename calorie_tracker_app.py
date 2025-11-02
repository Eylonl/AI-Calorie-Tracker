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
from supabase_client import SupabaseManager

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

# Initialize Supabase manager
if 'supabase_manager' not in st.session_state:
    st.session_state.supabase_manager = SupabaseManager()

# Initialize session state
if 'meal_history' not in st.session_state:
    st.session_state.meal_history = []
if 'daily_totals' not in st.session_state:
    st.session_state.daily_totals = {}
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'use_supabase' not in st.session_state:
    st.session_state.use_supabase = st.session_state.supabase_manager.is_connected()

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

def add_meal_to_history(meal_data, meal_type, photo_image=None):
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
    
    # Use Supabase if available
    if st.session_state.use_supabase:
        try:
            # Upload photo if provided
            photo_url = None
            if photo_image:
                temp_meal_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                photo_url = st.session_state.supabase_manager.upload_photo(photo_image, temp_meal_id)
            
            # Save to Supabase
            meal_id = st.session_state.supabase_manager.save_meal(meal_entry, photo_url)
            if meal_id:
                st.success("✅ Meal saved to cloud database!")
                # Refresh data from Supabase
                load_meals_from_supabase()
                return
            else:
                st.warning("Failed to save to cloud, using local storage as backup")
        except Exception as e:
            st.warning(f"Cloud save failed ({e}), using local storage")
    
    # Fallback to local storage
    st.session_state.meal_history.append(meal_entry)
    
    # Update daily totals
    if today not in st.session_state.daily_totals:
        st.session_state.daily_totals[today] = 0
    st.session_state.daily_totals[today] += meal_data['total_calories']
    
    save_meal_history()

def load_meals_from_supabase():
    """Load meals from Supabase database"""
    if not st.session_state.use_supabase:
        return
    
    try:
        meals = st.session_state.supabase_manager.get_meals()
        daily_totals = st.session_state.supabase_manager.get_daily_totals()
        
        # Convert Supabase format to local format
        converted_meals = []
        for meal in meals:
            converted_meal = {
                'id': meal['id'],  # Add Supabase ID for editing/deleting
                'date': meal['date'],
                'timestamp': meal['timestamp'],
                'meal_type': meal['meal_type'],
                'total_calories': meal['total_calories'],
                'notes': meal['notes'] or '',
                'photo_url': meal.get('photo_url'),
                'foods': meal.get('foods', [])
            }
            converted_meals.append(converted_meal)
        
        st.session_state.meal_history = converted_meals
        st.session_state.daily_totals = daily_totals
        
    except Exception as e:
        st.error(f"Error loading meals from Supabase: {e}")

def main():
    # Load meal history on startup
    if st.session_state.use_supabase:
        load_meals_from_supabase()
    else:
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
        
        # Database status
        st.header("Database Status")
        if st.session_state.use_supabase:
            st.success("☁️ Connected to Supabase Cloud")
            st.caption("✅ Photos saved • ✅ Data persistent • ✅ Cloud backup")
        else:
            st.warning("📱 Using Local Storage")
            st.caption("⚠️ No photos saved • ⚠️ Data may be lost on restart")
        
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
        
        # Manual entry option
        st.markdown("---")
        st.markdown("### ✏️ Manual Entry")
        st.markdown("*No photo? Enter your meal details manually*")
        
        if st.button("📝 Add Meal Manually", use_container_width=True):
            st.session_state.show_manual_entry = True
            st.rerun()
        
        # Manual entry form
        if st.session_state.get('show_manual_entry', False):
            st.markdown("#### 🍽️ Enter Meal Details")
            
            with st.form("manual_meal_entry"):
                # Date selection
                meal_date = st.date_input("📅 Meal Date", value=date.today())
                
                # Manual food entry
                st.markdown("**Add Food Items:**")
                
                # Initialize manual foods in session state
                if 'manual_foods' not in st.session_state:
                    st.session_state.manual_foods = [{"name": "", "portion": "", "calories": 0}]
                
                manual_foods = []
                total_manual_calories = 0
                
                for i in range(len(st.session_state.manual_foods)):
                    st.markdown(f"**Food Item {i+1}:**")
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        food_name = st.text_input("Food Name", key=f"manual_name_{i}", placeholder="e.g., Grilled Chicken")
                    with col2:
                        portion_size = st.text_input("Portion", key=f"manual_portion_{i}", placeholder="e.g., 150g")
                    with col3:
                        calories = st.number_input("Calories", min_value=0, key=f"manual_calories_{i}", value=0)
                    
                    if food_name:  # Only add if name is provided
                        manual_foods.append({
                            "name": food_name,
                            "portion_size": portion_size or "1 serving",
                            "calories": calories,
                            "confidence": 100  # Manual entry is 100% confident
                        })
                        total_manual_calories += calories
                
                # Buttons to add/remove food items
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("➕ Add Food Item"):
                        st.session_state.manual_foods.append({"name": "", "portion": "", "calories": 0})
                        st.rerun()
                
                with col2:
                    if len(st.session_state.manual_foods) > 1:
                        if st.form_submit_button("➖ Remove Last"):
                            st.session_state.manual_foods.pop()
                            st.rerun()
                
                # Notes
                manual_notes = st.text_area("📝 Notes (optional)", placeholder="Any additional details about the meal...")
                
                # Display total
                if total_manual_calories > 0:
                    st.markdown(f"### 🔥 Total Calories: **{total_manual_calories}**")
                
                # Save button
                if st.form_submit_button("✅ Save Manual Entry", type="primary", use_container_width=True):
                    if manual_foods and any(food['name'] for food in manual_foods):
                        # Create meal data structure
                        manual_meal_data = {
                            'foods': [food for food in manual_foods if food['name']],  # Filter out empty entries
                            'total_calories': total_manual_calories,
                            'notes': manual_notes
                        }
                        
                        # Add to history with custom date
                        meal_entry = {
                            'date': meal_date.isoformat(),
                            'timestamp': datetime.now().isoformat(),
                            'meal_type': meal_type,
                            'foods': manual_meal_data['foods'],
                            'total_calories': manual_meal_data['total_calories'],
                            'notes': manual_meal_data['notes']
                        }
                        
                        st.session_state.meal_history.append(meal_entry)
                        
                        # Update daily totals
                        date_str = meal_date.isoformat()
                        if date_str not in st.session_state.daily_totals:
                            st.session_state.daily_totals[date_str] = 0
                        st.session_state.daily_totals[date_str] += manual_meal_data['total_calories']
                        
                        save_meal_history()
                        
                        st.success(f"✅ Manual meal saved! Total calories: {total_manual_calories}")
                        
                        # Reset form
                        st.session_state.manual_foods = [{"name": "", "portion": "", "calories": 0}]
                        st.session_state.show_manual_entry = False
                        st.rerun()
                    else:
                        st.error("Please add at least one food item with a name.")
                
                # Cancel button
                if st.form_submit_button("❌ Cancel Manual Entry"):
                    st.session_state.manual_foods = [{"name": "", "portion": "", "calories": 0}]
                    st.session_state.show_manual_entry = False
                    st.rerun()
        
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
                        st.session_state.current_image = image_to_analyze  # Store image for Supabase
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
                        # Include photo if available
                        photo_image = st.session_state.get('current_image')
                        add_meal_to_history(confirmed_meal, st.session_state.current_meal_type, photo_image)
                        st.success(f"Meal saved! Total calories: {total_calories}")
                        
                        # Clean up session state
                        del st.session_state.current_analysis
                        del st.session_state.current_meal_type
                        if 'current_image' in st.session_state:
                            del st.session_state.current_image
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
                
                # Display each meal for this day with edit/delete options
                for meal_idx, meal in enumerate(daily_meals):
                    time_str = meal['timestamp'][11:16]  # Extract HH:MM
                    meal_id = f"{date_str}_{meal_idx}"  # Unique identifier for this meal
                    
                    with st.expander(f"{time_str} - {meal['meal_type']} ({meal['total_calories']:.0f} calories)"):
                        # Display photo if available
                        if meal.get('photo_url'):
                            st.markdown("**📸 Meal Photo:**")
                            try:
                                st.image(meal['photo_url'], caption=f"{meal['meal_type']} photo", use_column_width=True)
                            except Exception as e:
                                st.caption("📷 Photo unavailable")
                        
                        # Display meal details
                        st.write("**🍽️ Foods:**")
                        for food in meal['foods']:
                            st.write(f"- {food['name']}: {food['portion_size']} ({food['calories']} calories)")
                        if meal['notes']:
                            st.write(f"**📝 Notes:** {meal['notes']}")
                        
                        # Edit/Delete buttons
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✏️ Edit", key=f"edit_{meal_id}", use_container_width=True):
                                st.session_state.editing_meal = {
                                    'meal': meal,
                                    'date_str': date_str,
                                    'meal_idx': meal_idx
                                }
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_{meal_id}", use_container_width=True, type="secondary"):
                                # Delete from Supabase if available
                                if st.session_state.use_supabase and meal.get('id'):
                                    try:
                                        success = st.session_state.supabase_manager.delete_meal(meal['id'])
                                        if success:
                                            st.success(f"🗑️ Deleted {meal['meal_type']} ({meal['total_calories']} calories)")
                                            # Refresh data from Supabase
                                            load_meals_from_supabase()
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete meal from cloud database")
                                    except Exception as e:
                                        st.error(f"Error deleting meal: {e}")
                                else:
                                    # Fallback to local storage deletion
                                    meal_to_remove = None
                                    for i, hist_meal in enumerate(st.session_state.meal_history):
                                        if (hist_meal['date'] == date_str and 
                                            hist_meal['timestamp'] == meal['timestamp'] and
                                            hist_meal['meal_type'] == meal['meal_type']):
                                            meal_to_remove = i
                                            break
                                    
                                    if meal_to_remove is not None:
                                        # Remove from local history
                                        removed_meal = st.session_state.meal_history.pop(meal_to_remove)
                                        
                                        # Update daily totals
                                        st.session_state.daily_totals[date_str] -= removed_meal['total_calories']
                                        if st.session_state.daily_totals[date_str] <= 0:
                                            del st.session_state.daily_totals[date_str]
                                        
                                        save_meal_history()
                                        st.success(f"🗑️ Deleted {removed_meal['meal_type']} ({removed_meal['total_calories']} calories)")
                                        st.rerun()
                
                st.divider()  # Add separator between days
            
            # Edit meal form (appears when editing)
            if 'editing_meal' in st.session_state:
                st.markdown("---")
                st.markdown("### ✏️ Edit Meal")
                
                editing_data = st.session_state.editing_meal
                meal = editing_data['meal']
                
                with st.form("edit_meal_form"):
                    st.markdown(f"**Editing:** {meal['meal_type']} from {editing_data['date_str']}")
                    
                    # Edit meal type
                    new_meal_type = st.selectbox("Meal Type", 
                                               ["Breakfast", "Lunch", "Dinner", "Snack"], 
                                               index=["Breakfast", "Lunch", "Dinner", "Snack"].index(meal['meal_type']))
                    
                    # Edit date
                    current_date = datetime.fromisoformat(editing_data['date_str']).date()
                    new_date = st.date_input("Date", value=current_date)
                    
                    # Edit foods
                    st.markdown("**Edit Food Items:**")
                    edited_foods = []
                    total_edited_calories = 0
                    
                    # Initialize editing foods in session state if not exists
                    if 'editing_foods' not in st.session_state:
                        st.session_state.editing_foods = meal['foods'].copy()
                    
                    for i, food in enumerate(st.session_state.editing_foods):
                        st.markdown(f"**Food Item {i+1}:**")
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            food_name = st.text_input("Food Name", value=food['name'], key=f"edit_name_{i}")
                        with col2:
                            portion_size = st.text_input("Portion", value=food['portion_size'], key=f"edit_portion_{i}")
                        with col3:
                            calories = st.number_input("Calories", value=food['calories'], min_value=0, key=f"edit_calories_{i}")
                        
                        if food_name:  # Only add if name is provided
                            edited_foods.append({
                                "name": food_name,
                                "portion_size": portion_size,
                                "calories": calories,
                                "confidence": food.get('confidence', 100)
                            })
                            total_edited_calories += calories
                    
                    # Buttons to add/remove food items
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("➕ Add Food Item"):
                            st.session_state.editing_foods.append({
                                "name": "",
                                "portion_size": "1 serving",
                                "calories": 0,
                                "confidence": 100
                            })
                            st.rerun()
                    
                    with col2:
                        if len(st.session_state.editing_foods) > 1:
                            if st.form_submit_button("➖ Remove Last"):
                                st.session_state.editing_foods.pop()
                                st.rerun()
                    
                    # Edit notes
                    new_notes = st.text_area("Notes", value=meal.get('notes', ''))
                    
                    # Display total
                    if total_edited_calories > 0:
                        st.markdown(f"### 🔥 Total Calories: **{total_edited_calories}**")
                    
                    # Save/Cancel buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("✅ Save Changes", type="primary", use_container_width=True):
                            if edited_foods and any(food['name'] for food in edited_foods):
                                # Update in Supabase if available
                                if st.session_state.use_supabase and meal.get('id'):
                                    try:
                                        updated_meal_data = {
                                            'date': new_date.isoformat(),
                                            'meal_type': new_meal_type,
                                            'foods': [food for food in edited_foods if food['name']],
                                            'total_calories': total_edited_calories,
                                            'notes': new_notes
                                        }
                                        
                                        success = st.session_state.supabase_manager.update_meal(meal['id'], updated_meal_data)
                                        if success:
                                            st.success(f"✅ Meal updated! New total: {total_edited_calories} calories")
                                            # Refresh data from Supabase
                                            load_meals_from_supabase()
                                            # Clear editing state
                                            del st.session_state.editing_meal
                                            del st.session_state.editing_foods
                                            st.rerun()
                                        else:
                                            st.error("Failed to update meal in cloud database")
                                    except Exception as e:
                                        st.error(f"Error updating meal: {e}")
                                else:
                                    # Fallback to local storage update
                                    original_date = editing_data['date_str']
                                    meal_to_edit = None
                                    
                                    for i, hist_meal in enumerate(st.session_state.meal_history):
                                        if (hist_meal['date'] == original_date and 
                                            hist_meal['timestamp'] == meal['timestamp'] and
                                            hist_meal['meal_type'] == meal['meal_type']):
                                            meal_to_edit = i
                                            break
                                    
                                    if meal_to_edit is not None:
                                        # Remove old calories from daily totals
                                        st.session_state.daily_totals[original_date] -= st.session_state.meal_history[meal_to_edit]['total_calories']
                                        if st.session_state.daily_totals[original_date] <= 0:
                                            del st.session_state.daily_totals[original_date]
                                        
                                        # Update the meal
                                        new_date_str = new_date.isoformat()
                                        st.session_state.meal_history[meal_to_edit].update({
                                            'date': new_date_str,
                                            'meal_type': new_meal_type,
                                            'foods': [food for food in edited_foods if food['name']],
                                            'total_calories': total_edited_calories,
                                            'notes': new_notes
                                        })
                                        
                                        # Add new calories to daily totals
                                        if new_date_str not in st.session_state.daily_totals:
                                            st.session_state.daily_totals[new_date_str] = 0
                                        st.session_state.daily_totals[new_date_str] += total_edited_calories
                                        
                                        save_meal_history()
                                        st.success(f"✅ Meal updated! New total: {total_edited_calories} calories")
                                        
                                        # Clear editing state
                                        del st.session_state.editing_meal
                                        del st.session_state.editing_foods
                                        st.rerun()
                            else:
                                st.error("Please add at least one food item with a name.")
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state.editing_meal
                            if 'editing_foods' in st.session_state:
                                del st.session_state.editing_foods
                            st.rerun()
            
            # Daily summary chart
            if st.session_state.daily_totals:
                st.subheader("Daily Calorie Trends")
                df = pd.DataFrame(list(st.session_state.daily_totals.items()), columns=['Date', 'Calories'])
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                st.line_chart(df.set_index('Date'))

if __name__ == "__main__":
    main()
