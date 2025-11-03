// Serverless function for OpenAI photo analysis
// Deploy this to Vercel or Netlify

export default async function handler(req, res) {
    // Enable CORS for your PWA domain
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS, GET');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.setHeader('Access-Control-Max-Age', '86400');
    
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const { imageData } = req.body;
        
        if (!imageData) {
            return res.status(400).json({ error: 'No image data provided' });
        }
        
        // Check if OpenAI API key is configured
        if (!process.env.OPENAI_API_KEY) {
            return res.status(500).json({ 
                error: 'OpenAI API key not configured',
                details: 'Please set OPENAI_API_KEY environment variable in Vercel'
            });
        }
        
        // Initialize OpenAI with secret from environment
        const { OpenAI } = await import('openai');
        const openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY
        });
        
        // Analyze the image
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                {
                    role: "user",
                    content: [
                        {
                            type: "text",
                            text: "Analyze this food image and provide detailed nutrition information. Return a JSON object with: foods array (each with name, portion_size, calories, protein, carbs, fat, fiber, sugar, sodium, confidence), total_calories, and notes."
                        },
                        {
                            type: "image_url",
                            image_url: {
                                url: `data:image/jpeg;base64,${imageData}`
                            }
                        }
                    ]
                }
            ],
            max_tokens: 1000
        });
        
        // Parse the response
        const analysisText = response.choices[0].message.content;
        
        // Try to extract and parse JSON from the response
        let analysis;
        try {
            // First try to parse the entire response as JSON
            analysis = JSON.parse(analysisText);
        } catch (firstError) {
            try {
                // If that fails, look for JSON block in the response
                const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    let jsonString = jsonMatch[0];
                    // Clean up common JSON issues
                    jsonString = jsonString
                        .replace(/[\u0000-\u001F\u007F-\u009F]/g, '') // Remove control characters
                        .replace(/,\s*}/g, '}') // Remove trailing commas
                        .replace(/,\s*]/g, ']'); // Remove trailing commas in arrays
                    
                    analysis = JSON.parse(jsonString);
                } else {
                    throw new Error('No JSON found in response');
                }
            } catch (secondError) {
                console.error('JSON parsing failed:', secondError);
                console.error('Raw response:', analysisText);
                
                // Create fallback structured response
                analysis = {
                    foods: [{
                        name: "Food Item",
                        portion_size: "1 serving",
                        calories: 300,
                        protein: 15.0,
                        carbs: 30.0,
                        fat: 12.0,
                        fiber: 3.0,
                        sugar: 5.0,
                        sodium: 200.0,
                        confidence: 75
                    }],
                    total_calories: 300,
                    notes: `AI parsing failed. Raw response: ${analysisText.substring(0, 200)}...`
                };
            }
        }
        
        // Ensure all required fields exist and are properly formatted
        if (!analysis.foods || !Array.isArray(analysis.foods)) {
            analysis.foods = [];
        }
        
        // Clean up food items
        analysis.foods = analysis.foods.map(food => ({
            name: String(food.name || 'Unknown Food'),
            portion_size: String(food.portion_size || '1 serving'),
            calories: Number(food.calories) || 0,
            protein: Number(food.protein) || 0,
            carbs: Number(food.carbs) || 0,
            fat: Number(food.fat) || 0,
            fiber: Number(food.fiber) || 0,
            sugar: Number(food.sugar) || 0,
            sodium: Number(food.sodium) || 0,
            confidence: Number(food.confidence) || 50
        }));
        
        // Ensure total_calories is a number
        analysis.total_calories = Number(analysis.total_calories) || 0;
        
        // Ensure notes is a string
        analysis.notes = String(analysis.notes || '');
        
        return res.status(200).json(analysis);
        
    } catch (error) {
        console.error('OpenAI API error:', error);
        return res.status(500).json({ 
            error: 'Failed to analyze image',
            details: error.message 
        });
    }
}
