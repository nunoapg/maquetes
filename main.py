from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageFilter
import numpy as np
import uuid
import os
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.post("/gerar-maquete")
async def gerar_maquete(
    logo: UploadFile = File(...),
    produto: str = Form(...),
    pos_x: float = Form(50.0),
    pos_y: float = Form(50.0),
    tamanho: float = Form(30.0),
):
    try:
        # Load logo
        logo_bytes = await logo.read()
        logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

        # Remove black/white background from logo automatically
        logo_img = remover_fundo(logo_img)

        # Load product template
        produto_path = f"static/produtos/{produto}.png"
        if not os.path.exists(produto_path):
            return JSONResponse({"erro": "Produto não encontrado"}, status_code=404)

        produto_img = Image.open(produto_path).convert("RGBA")

        # Load product config (print area)
        config = PRODUTOS.get(produto)
        if not config:
            return JSONResponse({"erro": "Configuração não encontrada"}, status_code=404)

        # Calculate logo size and position within print area
        area = config["area"]
        area_w = area[2] - area[0]
        area_h = area[3] - area[1]

        logo_w = int(area_w * tamanho / 100)
        logo_h = int(logo_w * logo_img.height / logo_img.width)

        # Clamp logo height to area
        if logo_h > area_h * 0.9:
            logo_h = int(area_h * 0.9)
            logo_w = int(logo_h * logo_img.width / logo_img.height)

        logo_resized = logo_img.resize((logo_w, logo_h), Image.LANCZOS)

        # Position within print area
        max_x = area_w - logo_w
        max_y = area_h - logo_h
        paste_x = area[0] + int(max_x * pos_x / 100)
        paste_y = area[1] + int(max_y * pos_y / 100)

        # Composite
        result = produto_img.copy()
        result.paste(logo_resized, (paste_x, paste_y), logo_resized)

        # Save output
        output_id = str(uuid.uuid4())[:8]
        output_path = f"outputs/maquete_{output_id}.png"
        result.save(output_path, "PNG", dpi=(300, 300))

        return JSONResponse({
            "url": f"/outputs/maquete_{output_id}.png",
            "id": output_id,
            "dimensoes": config["dimensoes_reais"],
            "logo_cm": {
                "largura": round(logo_w / area_w * config["dimensoes_reais"]["area_largura_cm"], 1),
                "altura": round(logo_h / area_h * config["dimensoes_reais"]["area_altura_cm"], 1),
            }
        })

    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)


def remover_fundo(img: Image.Image) -> Image.Image:
    arr = np.array(img).astype(float)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]

    # Detect black background
    darkness = (r + g + b) / 3
    black_mask = darkness < 60
    if black_mask.sum() > (arr.shape[0] * arr.shape[1] * 0.1):
        alpha = np.clip((darkness - 50) / 40, 0, 1) * 255
        arr[:,:,3] = np.minimum(arr[:,:,3], alpha)
        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    # Detect white background
    whiteness = (r + g + b) / 3
    white_mask = (whiteness > 240) & (np.abs(r - g) < 15) & (np.abs(g - b) < 15)
    if white_mask.sum() > (arr.shape[0] * arr.shape[1] * 0.1):
        alpha = np.clip((255 - whiteness) / 20, 0, 1) * 255
        arr[:,:,3] = np.minimum(arr[:,:,3], alpha)
        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    return img


# Product configurations — add your products here
PRODUTOS = {
    "avental": {
        "area": [320, 200, 620, 500],  # x1, y1, x2, y2 in pixels
        "dimensoes_reais": {
            "produto_largura_cm": 60,
            "produto_altura_cm": 90,
            "area_largura_cm": 20,
            "area_altura_cm": 20,
        }
    },
    "caneca": {
        "area": [150, 120, 420, 320],
        "dimensoes_reais": {
            "produto_largura_cm": 25,
            "produto_altura_cm": 10,
            "area_largura_cm": 8,
            "area_altura_cm": 6,
        }
    },
    "saco": {
        "area": [200, 150, 500, 450],
        "dimensoes_reais": {
            "produto_largura_cm": 30,
            "produto_altura_cm": 35,
            "area_largura_cm": 15,
            "area_altura_cm": 15,
        }
    },
}
