from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables to store model and encoders
model = None
encoders = None
algorithm_mapping = None

# Mappings for each category (will be loaded from encoders)
file_size_mapping = {}
data_type_mapping = {}
required_speed_mapping = {}
required_security_level_mapping = {}
real_time_mapping = {}
connectivity_mapping = {}
cost_sensitivity_mapping = {}

def load_model_and_encoders():
    """Load the trained model and label encoders."""
    global model, encoders, algorithm_mapping
    global file_size_mapping, data_type_mapping, required_speed_mapping
    global required_security_level_mapping, real_time_mapping
    global connectivity_mapping, cost_sensitivity_mapping
    
    try:
        # Adjust paths as necessary for your deployment
        model_path = os.environ.get('MODEL_PATH', 'model/encryption_model.pkl')
        encoder_path = os.environ.get('ENCODER_PATH', 'model/label_encoders.pkl')
        
        # Load model and encoders
        model = joblib.load(model_path)
        encoders = joblib.load(encoder_path)
        
        logger.info("Model and encoders loaded successfully")
        
        # Create mappings from encoders
        for column in encoders:
            le = encoders[column]
            if column == 'File Size':
                file_size_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Data Type':
                data_type_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Required Speed':
                required_speed_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Required Security Level':
                required_security_level_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Real-Time Requirement':
                real_time_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Connectivity Type':
                connectivity_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Encryption Cost Sensitivity':
                cost_sensitivity_mapping = {cat: idx for idx, cat in enumerate(le.classes_)}
            elif column == 'Encryption Algorithm':
                algorithm_mapping = {idx: cat for idx, cat in enumerate(le.classes_)}
        
        logger.info("Category mappings created successfully")
        
    except Exception as e:
        logger.error(f"Error loading model or encoders: {str(e)}")
        raise

def map_categories(file_size, data_type, required_speed, security_level,
                   real_time, connectivity, cost_sensitivity):
    """Map input categories to their numerical values."""
    try:
        return [
            file_size_mapping.get(file_size),
            data_type_mapping.get(data_type),
            required_speed_mapping.get(required_speed),
            required_security_level_mapping.get(security_level),
            real_time_mapping.get(real_time),
            connectivity_mapping.get(connectivity),
            cost_sensitivity_mapping.get(cost_sensitivity)
        ]
    except Exception as e:
        logger.error(f"Error during category mapping: {str(e)}")
        raise ValueError(f"Invalid input category: {str(e)}")

def create_input_dataframe(mapped_values):
    """Create a DataFrame with the mapped values."""
    return pd.DataFrame([{
        'File Size': mapped_values[0],
        'Data Type': mapped_values[1],
        'Required Speed': mapped_values[2],
        'Required Security Level': mapped_values[3],
        'Real-Time Requirement': mapped_values[4],
        'Connectivity Type': mapped_values[5],
        'Encryption Cost Sensitivity': mapped_values[6]
    }])

def predict_encryption_algorithm(df):
    """Make a prediction using the loaded model."""
    try:
        # Check if any input values are None
        if df.isnull().values.any():
            missing_columns = df.columns[df.isnull().any()].tolist()
            raise ValueError(f"Missing or invalid values for: {', '.join(missing_columns)}")
        
        prediction = model.predict(df)
        predicted_algorithm = algorithm_mapping[prediction[0]]
        return predicted_algorithm
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to check if the API is running."""
    return jsonify({"status": "healthy", "model_loaded": model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to predict the encryption algorithm based on input parameters."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract parameters from the request
        file_size = data.get('file_size')
        data_type = data.get('data_type')
        required_speed = data.get('required_speed')
        security_level = data.get('security_level')
        real_time = data.get('real_time')
        connectivity = data.get('connectivity')
        cost_sensitivity = data.get('cost_sensitivity')
        
        # Check if all required parameters are provided
        required_params = ['file_size', 'data_type', 'required_speed', 
                          'security_level', 'real_time', 'connectivity', 'cost_sensitivity']
        missing_params = [param for param in required_params if data.get(param) is None]
        
        if missing_params:
            return jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}), 400
        
        # Map category values to their numerical representations
        try:
            mapped_values = map_categories(
                file_size, data_type, required_speed, security_level,
                real_time, connectivity, cost_sensitivity
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Create input DataFrame
        input_df = create_input_dataframe(mapped_values)
        
        # Make prediction
        try:
            algorithm = predict_encryption_algorithm(input_df)
            return jsonify({
                "predicted_algorithm": algorithm,
                "input_parameters": data
            })
        except Exception as e:
            return jsonify({"error": f"Prediction error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    # Load model and encoders on startup
    load_model_and_encoders()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)