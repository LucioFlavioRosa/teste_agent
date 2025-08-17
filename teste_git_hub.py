# -*- coding: utf-8 -*-
"""
Módulo de compatibilidade que expõe o app Flask.
A execução do servidor não ocorre em import. Para rodar o servidor diretamente,
execute este módulo como script ou utilize app.py.
"""

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
