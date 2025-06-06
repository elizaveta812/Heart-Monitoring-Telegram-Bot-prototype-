import joblib


class ModelHandler:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        # загрузка модели
        return joblib.load(model_path)

    def predict(self, features):
        # предсказание
        return self.model.predict(features)


# использование
if __name__ == "__main__":
    model_path = "models/mfdp_model.pkl"
    model_handler = ModelHandler(model_path)
