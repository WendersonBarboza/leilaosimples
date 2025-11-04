# Leilão (Flask)

Aplicação web simples de leilão com cadastro de usuários, itens e lances.

## Requisitos
- Python 3.10+

## Instalação
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar
```bash
python app.py
```
Abra http://localhost:5000 no navegador.

## Funcionalidades
- Cadastro de usuários
- Cadastro de itens de leilão (título, preço inicial, término)
- Página do item com lances e formulário para ofertar
- Validações e mensagens via flash

Observação: horários exibidos/armazenados estão em UTC.
