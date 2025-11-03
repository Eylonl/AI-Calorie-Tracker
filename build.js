#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function createStaticBuild() {
    console.log('Creating static build for CalorieAI...');
    
    // Create dist directory
    const distDir = 'dist';
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir);
    }
    
    // Copy essential files
    const filesToCopy = [
        'calorie_tracker_app.py',
        'supabase_client.py',
        'manifest.json',
        'requirements.txt'
    ];
    
    filesToCopy.forEach(file => {
        if (fs.existsSync(file)) {
            fs.copyFileSync(file, path.join(distDir, file));
            console.log(`Copied ${file}`);
        }
    });
    
    // Create HTML wrapper
    const htmlContent = `<!DOCTYPE html>
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
        setTimeout(() => {
            const iframe = document.getElementById('app-frame');
            const loading = document.getElementById('loading');
            
            // Your Streamlit app URL
            iframe.src = 'https://ai-calorie-tracker-eylonl.streamlit.app';
            
            iframe.onload = () => {
                loading.style.display = 'none';
                iframe.style.display = 'block';
            };
        }, 1000);
    </script>
</body>
</html>`;
    
    // Write HTML file
    fs.writeFileSync(path.join(distDir, 'index.html'), htmlContent);
    
    // Copy manifest if it exists
    if (fs.existsSync('manifest.json')) {
        fs.copyFileSync('manifest.json', path.join(distDir, 'manifest.json'));
    }
    
    console.log('Static build created successfully!');
    console.log('Files in dist:');
    fs.readdirSync(distDir).forEach(file => {
        console.log(`  - ${file}`);
    });
}

createStaticBuild();
