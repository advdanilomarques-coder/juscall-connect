# -*- coding: utf-8 -*-
"""
Garante a existência do usuário administrador padrão definido no .env.

Isso já acontece automaticamente ao subir o main.py, mas este script permite
rodar o mesmo passo isoladamente (usado pelo install-all.sh).
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings          # noqa: E402
from app.core.security import hash_password    # noqa: E402
from app.database.session import Base, SessionLocal, engine  # noqa: E402
from app.models.user import AdminUser           # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existente = db.query(AdminUser).filter(AdminUser.email == settings.ADMIN_DEFAULT_EMAIL).first()
        if existente:
            print(f"Administrador já existe: {settings.ADMIN_DEFAULT_EMAIL}")
            return

        admin = AdminUser(
            nome=settings.ADMIN_DEFAULT_NAME,
            email=settings.ADMIN_DEFAULT_EMAIL,
            senha_hash=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
            papel="admin",
            ativo=True,
        )
        db.add(admin)
        db.commit()
        print(f"Administrador criado com sucesso: {settings.ADMIN_DEFAULT_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
