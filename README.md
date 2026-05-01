# Simulador de Maquetes

Ferramenta web para clientes visualizarem o seu logo em produtos personalizados antes de encomendar.

## Como funciona

1. Cliente escolhe o produto (avental, caneca, saco)
2. Faz upload do logo
3. Ajusta posição e tamanho com sliders
4. Carrega "Gerar maquete" — o servidor processa em alta qualidade
5. Aprova ou ajusta novamente

---

## Deploy no Railway (passo a passo)

### 1. Faz upload deste projeto para o GitHub
- Vai a github.com → New repository → chama "maquetes"
- Faz upload de todos estes ficheiros

### 2. Cria conta no Railway
- Vai a railway.app
- "Login with GitHub"

### 3. Deploy
- New Project → Deploy from GitHub repo
- Escolhe o repositório "maquetes"
- Railway deteta automaticamente o Python e faz deploy

### 4. Adiciona os teus produtos
- Coloca as fotos dos produtos em `static/produtos/`
- Nomes: `avental.png`, `caneca.png`, `saco.png`
- Edita as coordenadas da área de impressão em `main.py` no dicionário `PRODUTOS`

---

## Adicionar um novo produto

Em `main.py`, no dicionário `PRODUTOS`, adiciona:

```python
"nome_produto": {
    "area": [x1, y1, x2, y2],  # coordenadas em pixeis da área de impressão
    "dimensoes_reais": {
        "produto_largura_cm": 30,
        "produto_altura_cm": 35,
        "area_largura_cm": 15,
        "area_altura_cm": 15,
    }
}
```

Para descobrir as coordenadas: abre a foto do produto no Paint ou Photoshop
e aponta os pixeis dos 4 cantos da área onde o logo pode ir.

---

## Estrutura do projeto

```
maquetes-project/
├── main.py              ← servidor Python (FastAPI)
├── requirements.txt     ← dependências Python
├── railway.json         ← configuração Railway
├── nixpacks.toml        ← configuração de build
├── static/
│   ├── index.html       ← frontend (interface do cliente)
│   └── produtos/        ← coloca aqui as fotos dos produtos
│       ├── avental.png
│       ├── caneca.png
│       └── saco.png
└── outputs/             ← maquetes geradas (automático)
```
