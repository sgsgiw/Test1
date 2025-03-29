from flask import Flask, render_template, request, jsonify
import os
import base64
import tempfile
from Chatnot import extract_text_from_image, chat_with_gemini, elements_dict

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Check if image was sent in the request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        # Create a temporary file to save the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
            image_file.save(temp_path)
        
        # Extract text from the image
        try:
            element_symbol = extract_text_from_image(temp_path)
            
            if not element_symbol:
                return jsonify({'error': 'No element symbol detected in the image'})
            
            # Clean up and process extracted symbol
            element_symbol = element_symbol.strip().upper()
            
            # Check if the extracted symbol matches known elements
            if element_symbol in elements_dict:
                # Get element information
                element_info = elements_dict[element_symbol]
                
                # Construct prompt for Gemini AI
                prompt = f"Please provide detailed information about the element: {element_info['name']}"
                
                # Get response from Gemini AI
                response = chat_with_gemini(prompt)
                
                return jsonify({
                    'element': f"{element_info['name']} ({element_info['symbol']})",
                    'details': response
                })
            else:
                return jsonify({'error': f"Element symbol '{element_symbol}' not found in our database"})
        
        except Exception as e:
            return jsonify({'error': f"Error processing image: {str(e)}"})
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Create templates folder if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Save index.html to templates folder
    with open('templates/index.html', 'w') as f:
        f.write(open('index.html').read())
    
    app.run(debug=True)
