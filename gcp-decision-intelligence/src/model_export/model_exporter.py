import joblib
import os

from src.storage import model_store


class ModelExporter:

    def export(

        self,

        model,

        model_name,

        feature_names=None,

        target_column=None,

        problem_type=None

    ):

        os.makedirs(model_store.LOCAL_MODEL_FOLDER, exist_ok=True)

        filename = os.path.join(
            model_store.LOCAL_MODEL_FOLDER,
            f"{model_name}.pkl"
        )

        package = {

            "model": model,

            "feature_names": feature_names,

            "target_column": target_column,

            "problem_type": problem_type

        }

        joblib.dump(package, filename)

        # No GCP (GCS_BUCKET definido) o modelo também é enviado ao bucket,
        # para sobreviver a reinícios e ficar visível em todas as instâncias.
        model_store.upload_model(filename)

        return filename
