import joblib


class ModelHandler:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    @staticmethod
    def load_model(model_path):
        # загрузка модели
        return joblib.load(model_path)

    def predict(self, features):
        # предсказание
        return self.model.predict(features)
