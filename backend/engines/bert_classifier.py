import torch
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np

class BertCommitmentClassifier:
    def __init__(self, model_name="cl-tohoku/bert-base-japanese-whole-word-masking"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_model(self):
        """
        Load the pre-trained BERT model.
        We might fine-tune this later with the 'several hundred labeled samples' mentioned by the user.
        """
        print(f"Loading BERT model: {self.model_name}...")
        try:
            self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
            self.model = BertForSequenceClassification.from_pretrained(self.model_name, num_labels=3) # Low, Medium, High
            self.model.to(self.device)
            self.model.eval()
            print("✅ BERT model loaded.")
        except Exception as e:
            print(f"❌ Failed to load BERT: {e}")

    def predict_commitment(self, text: str) -> dict:
        """
        Predict the commitment level (0-100 score equivalent) from text.
        """
        if not self.model:
            self.load_model()
            
        if not self.model:
            return {"score": 0, "label": "Error"}
            
        inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Mock mapping for now until fine-tuned
        # 0: Low, 1: Medium, 2: High
        score_map = {0: 5, 1: 15, 2: 25} 
        predicted_class = torch.argmax(probs).item()
        confidence = probs[0][predicted_class].item()
        
        return {
            "score": score_map.get(predicted_class, 0),
            "label": ["Low", "Medium", "High"][predicted_class],
            "confidence": confidence
        }
