import joblib


class ModelHandler:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        # Загрузка модели
        return joblib.load(model_path)  # или keras.models.load_model(model_path)

    def predict(self, features):
        # Предсказание
        return self.model.predict(features)
