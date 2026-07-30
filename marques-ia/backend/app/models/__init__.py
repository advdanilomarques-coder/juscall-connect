# -*- coding: utf-8 -*-
"""
Importa todos os modelos em um único lugar, garantindo que fiquem registrados
na Base declarativa antes de Base.metadata.create_all() ser chamado.
"""
from app.models.audit_log import LogAuditoria      # noqa: F401
from app.models.case import Caso                    # noqa: F401
from app.models.client import Cliente                # noqa: F401
from app.models.contract import Contrato             # noqa: F401
from app.models.document import Documento            # noqa: F401
from app.models.knowledge import BaseConhecimento    # noqa: F401
from app.models.message import Mensagem              # noqa: F401
from app.models.user import AdminUser                # noqa: F401
