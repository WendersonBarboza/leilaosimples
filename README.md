# Leilão (Desktop - Tkinter)

Aplicativo desktop simples de leilões com autenticação, criação de leilões e lances, utilizando Tkinter.

## Requisitos
- Python 3.10+

## Instalação (opcional)
Recomendado criar ambiente virtual e instalar dependências (não é obrigatório para o Tkinter):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar (Aplicativo Desktop)
```bash
python main.py
```
Isso abrirá a janela do aplicativo no seu computador (não usa navegador).

## Funcionalidades
- Cadastro e login de usuários
- Criação de leilões (título, descrição, preço inicial)
- Listagem de leilões e registro de lances
- Fechamento de leilão pelo dono

Dados são salvos em `auctions_data.json` na pasta do projeto.
