"""
Camada de persistência com dois backends:

* SQLite (padrão, desenvolvimento local) -> arquivo ``business_ai.db``
* PostgreSQL / Cloud SQL (produção no GCP) -> ativado quando
  ``DATABASE_URL`` ou ``INSTANCE_CONNECTION_NAME`` estiver definido.

Variáveis de ambiente suportadas:

    DATABASE_URL              postgresql://user:pass@host:5432/dbname
    INSTANCE_CONNECTION_NAME  projeto:regiao:instancia (Cloud SQL via socket)
    DB_USER / DB_PASS / DB_NAME
    SQLITE_PATH               caminho do arquivo SQLite (padrão business_ai.db)

A API pública (save_upload, get_models, create_user, ...) é idêntica à
versão original, então as páginas Streamlit não precisam mudar.
"""

import os
import sqlite3
import threading
from datetime import datetime


_LOCK = threading.RLock()
_SHARED = {"connection": None, "backend": None, "initialized": False}


def _postgres_conninfo():

    url = os.getenv("DATABASE_URL")

    if url:
        return url

    instance = os.getenv("INSTANCE_CONNECTION_NAME")

    if not instance:
        return None

    socket_dir = os.getenv("DB_SOCKET_DIR", "/cloudsql")

    return " ".join([
        f"host={socket_dir}/{instance}",
        f"dbname={os.getenv('DB_NAME', 'business_ai')}",
        f"user={os.getenv('DB_USER', 'postgres')}",
        f"password={os.getenv('DB_PASS', '')}",
    ])


def _connect():

    conninfo = _postgres_conninfo()

    if conninfo:

        import psycopg

        connection = psycopg.connect(conninfo, autocommit=True)

        return connection, "postgres"

    connection = sqlite3.connect(
        os.getenv("SQLITE_PATH", "business_ai.db"),
        check_same_thread=False
    )

    return connection, "sqlite"


def _is_closed(connection, backend):

    if connection is None:
        return True

    if backend == "postgres":
        return connection.closed or connection.broken

    return False


class Database:

    def __init__(self):

        with _LOCK:

            if _is_closed(_SHARED["connection"], _SHARED["backend"]):
                (
                    _SHARED["connection"],
                    _SHARED["backend"]
                ) = _connect()
                _SHARED["initialized"] = False

            self.connection = _SHARED["connection"]
            self.backend = _SHARED["backend"]

            if not _SHARED["initialized"]:
                self.create_tables()
                self.ensure_user_columns()
                _SHARED["initialized"] = True

    # ==================================================
    # HELPERS
    # ==================================================

    @property
    def is_postgres(self):

        return self.backend == "postgres"

    def _sql(self, query):

        # SQLite usa "?" como placeholder; psycopg usa "%s".
        if self.is_postgres:
            return query.replace("?", "%s")

        return query

    def _execute(self, query, params=(), fetch=None):

        with _LOCK:

            cursor = self.connection.cursor()

            try:
                cursor.execute(self._sql(query), params)

                if fetch == "one":
                    result = cursor.fetchone()
                elif fetch == "all":
                    result = cursor.fetchall()
                else:
                    result = None

                if not self.is_postgres:
                    self.connection.commit()

                return result

            finally:
                cursor.close()

    # ==================================================
    # CREATE TABLES
    # ==================================================

    def create_tables(self):

        if self.is_postgres:
            pk = "SERIAL PRIMARY KEY"
            blob = "BYTEA"
        else:
            pk = "INTEGER PRIMARY KEY AUTOINCREMENT"
            blob = "BLOB"

        self._execute(f"""
            CREATE TABLE IF NOT EXISTS uploads(
                id {pk},
                filename TEXT,
                rows INTEGER,
                columns INTEGER,
                dataset_type TEXT,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self._execute(f"""
            CREATE TABLE IF NOT EXISTS model_history(
                id {pk},
                dataset_name TEXT,
                model_name TEXT,
                score REAL,
                problem_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self._execute(f"""
            CREATE TABLE IF NOT EXISTS prediction_history(
                id {pk},
                model_name TEXT,
                filename TEXT,
                rows INTEGER,
                prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self._execute(f"""
            CREATE TABLE IF NOT EXISTS users(
                id {pk},
                username TEXT UNIQUE,
                password {blob},
                email TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)

    # ==================================================
    # ENSURE OLD DATABASES HAVE NEW USER COLUMNS
    # ==================================================

    def ensure_user_columns(self):

        if self.is_postgres:
            columns = self._execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
            """, fetch="all")
            existing_columns = [column[0] for column in columns]
        else:
            columns = self._execute(
                "PRAGMA table_info(users)",
                fetch="all"
            )
            existing_columns = [column[1] for column in columns]

        for name in ("email", "registered_at", "last_login"):

            if name not in existing_columns:

                column_type = "TEXT" if name == "email" else "TIMESTAMP"

                self._execute(
                    f"ALTER TABLE users ADD COLUMN {name} {column_type}"
                )

    # ==================================================
    # UPLOAD HISTORY
    # ==================================================

    def save_upload(
        self,
        filename,
        rows,
        columns,
        dataset_type
    ):

        self._execute("""
            INSERT INTO uploads(
                filename,
                rows,
                columns,
                dataset_type
            )
            VALUES (?, ?, ?, ?)
        """, (
            filename,
            int(rows),
            int(columns),
            dataset_type
        ))

    def get_uploads(self):

        return self._execute("""
            SELECT *
            FROM uploads
            ORDER BY id DESC
        """, fetch="all")

    # ==================================================
    # MODEL HISTORY
    # ==================================================

    def save_model(
        self,
        dataset_name,
        model_name,
        score,
        problem_type
    ):

        self._execute("""
            INSERT INTO model_history(
                dataset_name,
                model_name,
                score,
                problem_type
            )
            VALUES (?, ?, ?, ?)
        """, (
            dataset_name,
            model_name,
            float(score) if score is not None else None,
            problem_type
        ))

    def get_models(self):

        return self._execute("""
            SELECT *
            FROM model_history
            ORDER BY id DESC
        """, fetch="all")

    # ==================================================
    # PREDICTION HISTORY
    # ==================================================

    def save_prediction(
        self,
        model_name,
        filename,
        rows
    ):

        self._execute("""
            INSERT INTO prediction_history(
                model_name,
                filename,
                rows
            )
            VALUES (?, ?, ?)
        """, (
            model_name,
            filename,
            int(rows)
        ))

    def get_predictions(self):

        return self._execute("""
            SELECT *
            FROM prediction_history
            ORDER BY id DESC
        """, fetch="all")

    # ==================================================
    # USER AUTHENTICATION
    # ==================================================

    def create_user(
        self,
        username,
        password,
        email
    ):

        self._execute("""
            INSERT INTO users(
                username,
                password,
                email,
                registered_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            password,
            email,
            datetime.now()
        ))

    @staticmethod
    def _normalize_user(row):

        # BYTEA no PostgreSQL volta como memoryview; bcrypt espera bytes.
        if row is None:
            return None

        return tuple(
            bytes(value) if isinstance(value, memoryview) else value
            for value in row
        )

    # ==================================================
    # GET USER BY USERNAME
    # ==================================================

    def get_user(
        self,
        username
    ):

        return self._normalize_user(self._execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """, (
            username,
        ), fetch="one"))

    # ==================================================
    # GET USER BY EMAIL
    # ==================================================

    def get_user_by_email(
        self,
        email
    ):

        return self._normalize_user(self._execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (
            email,
        ), fetch="one"))

    # ==================================================
    # GET USER PROFILE
    # ==================================================

    def get_user_profile(
        self,
        username
    ):

        return self._execute("""
            SELECT
                id,
                username,
                email,
                registered_at,
                last_login
            FROM users
            WHERE username = ?
        """, (
            username,
        ), fetch="one")

    # ==================================================
    # UPDATE LAST LOGIN
    # ==================================================

    def update_last_login(
        self,
        username
    ):

        self._execute("""
            UPDATE users
            SET last_login = ?
            WHERE username = ?
        """, (
            datetime.now(),
            username
        ))

    # ==================================================
    # CLOSE DATABASE
    # ==================================================

    def close(self):

        # A conexão é compartilhada pelo processo; fechar aqui derrubaria
        # as outras sessões do Streamlit. Mantido por compatibilidade.
        pass
