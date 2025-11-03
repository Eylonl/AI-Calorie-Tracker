#!/usr/bin/env python3
"""
Build script to create a static version of the Streamlit app for Capacitor
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_static_build():
    """Create a static build of the Streamlit app"""
    
    # Create dist directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy essential files
    files_to_copy = [
        "calorie_tracker_app.py",
        "supabase_client.py", 
        "manifest.json",
        "requirements.txt"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, dist_dir / file)
    
    # Create a simple HTML wrapper
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="CalorieAI">
    <title>CalorieAI</title>
    <link rel="manifest" href="./manifest.json">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #667eea;
            color: white;
            font-size: 18px;
        }
        iframe {
            width: 100%;
            height: 100vh;
            border: none;
        }
    </style>
</head>
<body>
    <div class="loading" id="loading">
        <div>Loading CalorieAI...</div>
    </div>
    <iframe id="app-frame" src="about:blank" style="display: none;"></iframe>
    
    <script>
        // In a real implementation, this would load your Streamlit app
        // For now, we'll redirect to the deployed version
        setTimeout(() => {
            const iframe = document.getElementById('app-frame');
            const loading = document.getElementById('loading');
            
            // Replace with your actual Streamlit Community Cloud URL
            iframe.src = 'https://your-streamlit-app-url.streamlit.app';
            
            iframe.onload = () => {
                loading.style.display = 'none';
                iframe.style.display = 'block';
            };
        }, 1000);
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(dist_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Copy manifest
    if Path("manifest.json").exists():
        shutil.copy2("manifest.json", dist_dir / "manifest.json")
    
    print("Static build created in 'dist' directory")
    print("Files included:")
    for file in dist_dir.iterdir():
        print(f"   - {file.name}")

if __name__ == "__main__":
    create_static_build()
