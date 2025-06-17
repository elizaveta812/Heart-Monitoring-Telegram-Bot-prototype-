import joblib
import os


class SingletonModelHandler:
    _instance = None

    def __new__(cls, model_path):
        if cls._instance is None:
            cls._instance = super(SingletonModelHandler, cls).__new__(cls)
            cls._instance.model = cls._instance.load_model(model_path)
        return cls._instance

    @staticmethod
    def load_model(model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        return joblib.load(model_path)

    def predict(self, features):
        return self.model.predict(features)
