import shap


class SHAPExplainer:

    def __init__(self, model):

        self.model = model

    def explain(self, X):

        explainer = shap.Explainer(self.model)

        shap_values = explainer(X)

        return shap_values