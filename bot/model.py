import joblib
import os


class ModelHandler:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model = self.load_model(model_path)

    @staticmethod
    def load_model(model_path):
        return joblib.load(model_path)

    def predict(self, features):
        return self.model.predict(features)
