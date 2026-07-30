"""Implementações concretas de provedores de IA.

Cada arquivo aqui implementa a interface `AIProvider` para um modelo
específico. Adicionar um novo modelo = adicionar um novo arquivo aqui e
registrá-lo no `AIManager`.

Os SDKs de cada provedor são importados de forma LAZY (dentro dos métodos),
para que a aplicação suba mesmo que nem todos os SDKs estejam instalados —
apenas o provedor efetivamente acionado precisa da sua biblioteca.
"""
