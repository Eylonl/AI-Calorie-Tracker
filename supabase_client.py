"""
Supabase client for AI Calorie Tracker
Handles all database operations and photo storage
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date
import uuid
import io
from PIL import Image

class SupabaseManager:
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Supabase client with credentials from secrets"""
        try:
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_ANON_KEY"]
            self.client: Client = create_client(supabase_url, supabase_key)
            return True
        except Exception as e:
            st.error(f"Failed to connect to Supabase: {e}")
            return False
    
    def is_connected(self):
        """Check if Supabase client is properly initialized"""
        return self.client is not None
    
    def upload_photo(self, image: Image.Image, meal_id: str) -> str:
        """Upload meal photo to Supabase Storage"""
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Generate unique filename
            filename = f"{meal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Upload to Supabase Storage
            response = self.client.storage.from_("meal-photos").upload(
                filename, 
                img_byte_arr.getvalue(),
                file_options={"content-type": "image/jpeg"}
            )
            
            # Check if upload was successful
            if hasattr(response, 'status_code') and response.status_code == 200:
                # Get public URL
                photo_url = self.client.storage.from_("meal-photos").get_public_url(filename)
                return photo_url
            elif not hasattr(response, 'status_code'):
                # Supabase Python client returns different response format
                # If no error, assume success and get public URL
                photo_url = self.client.storage.from_("meal-photos").get_public_url(filename)
                return photo_url
            else:
                st.error(f"Failed to upload photo: {response}")
                return None
                
        except Exception as e:
            st.error(f"Error uploading photo: {e}")
            return None
    
    def save_meal(self, meal_data: dict, photo_url: str = None) -> str:
        """Save meal to Supabase database"""
        try:
            # Generate meal ID
            meal_id = str(uuid.uuid4())
            
            # Prepare meal data
            meal_record = {
                "id": meal_id,
                "user_id": "default_user",  # For future user authentication
                "date": meal_data["date"],
                "timestamp": meal_data["timestamp"],
                "meal_type": meal_data["meal_type"],
                "total_calories": meal_data["total_calories"],
                "notes": meal_data.get("notes", ""),
                "photo_url": photo_url
            }
            
            # Insert meal
            meal_response = self.client.table("meals").insert(meal_record).execute()
            
            if meal_response.data:
                # Insert foods
                foods_data = []
                for food in meal_data["foods"]:
                    foods_data.append({
                        "meal_id": meal_id,
                        "name": food["name"],
                        "portion_size": food["portion_size"],
                        "calories": food["calories"],
                        "protein": food.get("protein", 0),
                        "carbs": food.get("carbs", 0),
                        "fat": food.get("fat", 0),
                        "fiber": food.get("fiber", 0),
                        "sugar": food.get("sugar", 0),
                        "sodium": food.get("sodium", 0),
                        "confidence": food.get("confidence", 100)
                    })
                
                if foods_data:
                    self.client.table("foods").insert(foods_data).execute()
                
                return meal_id
            else:
                st.error("Failed to save meal to database")
                return None
                
        except Exception as e:
            st.error(f"Error saving meal: {e}")
            return None
    
    def get_meals(self, start_date: date = None, end_date: date = None, meal_type: str = None):
        """Retrieve meals from Supabase database"""
        try:
            query = self.client.table("meals").select("""
                *,
                foods (
                    id,
                    name,
                    portion_size,
                    calories,
                    protein,
                    carbs,
                    fat,
                    fiber,
                    sugar,
                    sodium,
                    confidence
                )
            """).eq("user_id", "default_user").order("timestamp", desc=True)
            
            # Apply filters
            if start_date:
                query = query.gte("date", start_date.isoformat())
            if end_date:
                query = query.lte("date", end_date.isoformat())
            if meal_type and meal_type != "All":
                query = query.eq("meal_type", meal_type)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            st.error(f"Error retrieving meals: {e}")
            return []
    
    def update_meal(self, meal_id: str, meal_data: dict):
        """Update existing meal in database"""
        try:
            # Update meal record
            meal_update = {
                "date": meal_data["date"],
                "meal_type": meal_data["meal_type"],
                "total_calories": meal_data["total_calories"],
                "notes": meal_data.get("notes", "")
            }
            
            meal_response = self.client.table("meals").update(meal_update).eq("id", meal_id).execute()
            
            if meal_response.data:
                # Delete existing foods and insert new ones
                self.client.table("foods").delete().eq("meal_id", meal_id).execute()
                
                foods_data = []
                for food in meal_data["foods"]:
                    foods_data.append({
                        "meal_id": meal_id,
                        "name": food["name"],
                        "portion_size": food["portion_size"],
                        "calories": food["calories"],
                        "protein": food.get("protein", 0),
                        "carbs": food.get("carbs", 0),
                        "fat": food.get("fat", 0),
                        "fiber": food.get("fiber", 0),
                        "sugar": food.get("sugar", 0),
                        "sodium": food.get("sodium", 0),
                        "confidence": food.get("confidence", 100)
                    })
                
                if foods_data:
                    self.client.table("foods").insert(foods_data).execute()
                
                return True
            else:
                st.error("Failed to update meal")
                return False
                
        except Exception as e:
            st.error(f"Error updating meal: {e}")
            return False
    
    def delete_meal(self, meal_id: str):
        """Delete meal from database (foods will be deleted automatically due to CASCADE)"""
        try:
            response = self.client.table("meals").delete().eq("id", meal_id).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error deleting meal: {e}")
            return False
    
    def get_daily_totals(self, start_date: date = None, end_date: date = None):
        """Get daily calorie totals"""
        try:
            query = self.client.table("meals").select("date, total_calories").eq("user_id", "default_user")
            
            if start_date:
                query = query.gte("date", start_date.isoformat())
            if end_date:
                query = query.lte("date", end_date.isoformat())
            
            response = query.execute()
            
            # Aggregate by date
            daily_totals = {}
            for meal in response.data:
                date_str = meal["date"]
                if date_str not in daily_totals:
                    daily_totals[date_str] = 0
                daily_totals[date_str] += meal["total_calories"]
            
            return daily_totals
            
        except Exception as e:
            st.error(f"Error getting daily totals: {e}")
            return {}
    
    def migrate_from_json(self, json_data: dict):
        """Migrate existing JSON data to Supabase"""
        try:
            migrated_count = 0
            for meal in json_data.get("meals", []):
                # Convert to Supabase format
                meal_data = {
                    "date": meal["date"],
                    "timestamp": meal["timestamp"],
                    "meal_type": meal["meal_type"],
                    "total_calories": meal["total_calories"],
                    "notes": meal.get("notes", ""),
                    "foods": meal["foods"]
                }
                
                meal_id = self.save_meal(meal_data)
                if meal_id:
                    migrated_count += 1
            
            return migrated_count
            
        except Exception as e:
            st.error(f"Error migrating data: {e}")
            return 0
