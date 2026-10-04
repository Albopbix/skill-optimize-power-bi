import bcrypt


class Auth:

    # ==================================================
    # Hash Password
    # ==================================================

    def hash_password(self, password):

        if not isinstance(password, str):
            password = str(password)

        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

    # ==================================================
    # Verify Password
    # ==================================================

    def verify_password(
        self,
        password,
        hashed
    ):

        try:

            if not isinstance(password, str):
                password = str(password)

            # SQLite may return password as bytes
            if isinstance(hashed, str):
                hashed = hashed.encode("utf-8")

            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed
            )

        except Exception:

            return False