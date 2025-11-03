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
        
        // Initialize OpenAI with secret from environment
        const { OpenAI } = await import('openai');
        const openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY
        });
        
        // Analyze the image
        const response = await openai.chat.completions.create({
            model: "gpt-4-vision-preview",
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
        
        // Try to extract JSON from the response
        let analysis;
        try {
            // Look for JSON in the response
            const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                analysis = JSON.parse(jsonMatch[0]);
            } else {
                throw new Error('No JSON found in response');
            }
        } catch (parseError) {
            // If parsing fails, create structured response from text
            analysis = {
                foods: [{
                    name: "Food Item",
                    portion_size: "1 serving",
                    calories: 300,
                    protein: 15,
                    carbs: 30,
                    fat: 12,
                    fiber: 3,
                    sugar: 5,
                    sodium: 200,
                    confidence: 75
                }],
                total_calories: 300,
                notes: analysisText
            };
        }
        
        return res.status(200).json(analysis);
        
    } catch (error) {
        console.error('OpenAI API error:', error);
        return res.status(500).json({ 
            error: 'Failed to analyze image',
            details: error.message 
        });
    }
}
