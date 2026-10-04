"""
Armazenamento de modelos treinados (.pkl).

* Local (padrão): pasta ``saved_models/``.
* Google Cloud Storage: ativado quando ``GCS_BUCKET`` estiver definido.
  Os modelos ficam em ``gs://$GCS_BUCKET/$GCS_MODEL_PREFIX/<nome>.pkl``
  (prefixo padrão ``saved_models``) e são baixados para a pasta local,
  que passa a funcionar como cache. Isso é necessário no Cloud Run, cujo
  disco é efêmero e não é compartilhado entre instâncias.
"""

import os


LOCAL_MODEL_FOLDER = os.getenv("LOCAL_MODEL_FOLDER", "saved_models")


def _bucket():

    name = os.getenv("GCS_BUCKET")

    if not name:
        return None

    from google.cloud import storage

    return storage.Client().bucket(name)


def _prefix():

    return os.getenv("GCS_MODEL_PREFIX", "saved_models").strip("/")


def uses_gcs():

    return bool(os.getenv("GCS_BUCKET"))


def upload_model(local_path):

    bucket = _bucket()

    if bucket is None:
        return local_path

    blob_name = f"{_prefix()}/{os.path.basename(local_path)}"
    bucket.blob(blob_name).upload_from_filename(local_path)

    return f"gs://{bucket.name}/{blob_name}"


def list_models():

    """Lista nomes de arquivos .pkl disponíveis (GCS ou local)."""

    bucket = _bucket()

    if bucket is not None:

        prefix = f"{_prefix()}/"

        names = {
            blob.name[len(prefix):]
            for blob in bucket.list_blobs(prefix=prefix)
            if blob.name.lower().endswith(".pkl")
            and "/" not in blob.name[len(prefix):]
        }

        return sorted(names)

    if not os.path.isdir(LOCAL_MODEL_FOLDER):
        return []

    return sorted(
        name for name in os.listdir(LOCAL_MODEL_FOLDER)
        if name.lower().endswith(".pkl")
        and os.path.isfile(os.path.join(LOCAL_MODEL_FOLDER, name))
    )


def get_model_path(name):

    """Retorna um caminho local para o modelo, baixando do GCS se preciso."""

    name = os.path.basename(name)
    local_path = os.path.join(LOCAL_MODEL_FOLDER, name)

    bucket = _bucket()

    if bucket is not None:
        os.makedirs(LOCAL_MODEL_FOLDER, exist_ok=True)
        bucket.blob(f"{_prefix()}/{name}").download_to_filename(local_path)

    return local_path
