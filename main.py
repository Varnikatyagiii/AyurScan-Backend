from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image
import io
import json
import os
from huggingface_hub import hf_hub_download

app = FastAPI(title="AyurScan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model from Hugging Face
print("Downloading model from Hugging Face...")
model_path = hf_hub_download(
    repo_id="varnikatyagiii/AyurScan-Backend",
    filename="ayurscan_81percent_BEST.h5",
    token=os.environ.get("HF_TOKEN")
)
model = tf.keras.models.load_model(model_path)
print("Model loaded!")

with open('merged_database.json', 'r') as f:
    ayurvedic_db = json.load(f)
print("Database loaded!")

class_names = ['Aloe_Vera', 'Amla', 'Ashwagandha', 'Brahmi',
               'Curry_Leaf', 'Giloy', 'Moringa', 'Neem', 'Tulsi', 'Turmeric']

db_key_mapping = {
    'Aloe_Vera': 'Aloe Vera', 'Amla': 'Amla',
    'Ashwagandha': 'Ashwagandha', 'Brahmi': 'Brahmi',
    'Curry_Leaf': 'Curry Leaf', 'Giloy': 'Giloy',
    'Moringa': 'Moringa', 'Neem': 'Neem',
    'Tulsi': 'Tulsi', 'Turmeric': 'Turmeric'
}

@app.get("/")
def home():
    return {
        "message": "AyurScan API is running!",
        "team": "Team Royalance",
        "accuracy": "81.79%",
        "plants": class_names
    }

@app.post("/scan")
async def scan_plant(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        predictions = model.predict(img_array)
        predicted_class = class_names[np.argmax(predictions)]
        confidence = float(np.max(predictions)) * 100
        db_key = db_key_mapping.get(predicted_class, predicted_class)
        plant_info = ayurvedic_db.get(db_key, {})
        if confidence < 60:
            return {
                "success": False,
                "message": "Plant not recognized clearly. Please try again.",
                "confidence": confidence
            }
        return {
            "success": True,
            "plant_name": predicted_class,
            "confidence": round(confidence, 2),
            "scientific_name": plant_info.get("scientific_name", ""),
            "ayurvedic_benefits": plant_info.get("ayurvedic_benefits", []),
            "toxicity": plant_info.get("toxicity", {}),
            "allergy_risks": plant_info.get("allergy_risks", []),
            "how_to_use": plant_info.get("how_to_use", {}),
            "dosage": plant_info.get("dosage", {})
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
