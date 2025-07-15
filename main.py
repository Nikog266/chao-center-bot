# bot.py
import config
import json
import os
import random
import requests
import discord
import asyncio
from discord.ext import commands
from discord.ui import View, button, Button
from datetime import datetime

def actualizar_hambre(user_id):
    """
    Sube el hambre de un Chao según las horas que pasaron.
    +2 de hambre por hora.
    Máx. hambre: 100.
    """
    chao = chaos_data[user_id]

    if "last_meal" not in chao:
        chao["last_meal"] = datetime.datetime.utcnow().isoformat()

    try:
        last = datetime.datetime.fromisoformat(chao["last_meal"])
    except ValueError:
        last = datetime.datetime.utcnow()

    now = datetime.datetime.utcnow()
    horas = (now - last).total_seconds() / 3600
    incremento = int(horas * 2)

    if incremento > 0:
        chao["hunger"] = min(100, chao["hunger"] + incremento)
        chao["last_meal"] = now.isoformat()

# Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

# ==========================
# Cargar datos
# ==========================
def cargar_json(nombre_archivo):
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "r") as f:
            return json.load(f)
    return {}

chaos_data = cargar_json("chaos.json")
economy = cargar_json("economy.json")
last_claim = cargar_json("last_claim.json")

# ==========================
# Guardar datos
# ==========================
def guardar_json(nombre_archivo, data):
    with open(nombre_archivo, "w") as f:
        json.dump(data, f, indent=4)

def guardar_chaos():
    guardar_json("chaos.json", chaos_data)

def guardar_economy():
    guardar_json("economy.json", economy)

def guardar_last_claim():
    guardar_json("last_claim.json", last_claim)

# ==========================
# Recursos
# ==========================
CHAO_IMAGES = {
    "Normal": "https://static.wikia.nocookie.net/sonic/images/b/bf/NormalChao.png",
    "Hero": "https://static.wikia.nocookie.net/sonic/images/2/24/Chao_happy.png",
    "Dark": "https://static.wikia.nocookie.net/sonic/images/6/6b/Chao_angry.png"
}

# ==========================
# Datos de tienda
# ==========================
BLACKMARKET_ITEMS = [
    {"name": "Yellow Chaos Drive", "description": "Un potenciador misterioso que mejora Swim.", "price": 30},
    {"name": "Purple Chaos Drive", "description": "Un potenciador misterioso que mejora Fly.", "price": 30},
    {"name": "Green Chaos Drive", "description": "Un potenciador misterioso que mejora Run.", "price": 30},
    {"name": "Red Chaos Drive", "description": "Un potenciador misterioso que mejora Power.", "price": 30}
]

MEAL_ITEMS = [
    {
        "name": "Regular Fruit",
        "description": "Una fruta común que calma un poco el hambre.",
        "price": 10
    },
    {
        "name": "Hero Fruit",
        "description": "Incrementa la alineación positiva de tu Chao.",
        "price": 50
    },
    {
        "name": "Dark Fruit",
        "description": "Incrementa la alineación negativa de tu Chao.",
        "price": 50
    },
    {
        "name": "Round Fruit",
        "description": "Una fruta redonda que alimenta bastante.",
        "price": 15
    },
    {
        "name": "Triangular Fruit",
        "description": "Su forma curiosa le encanta al Chao.",
        "price": 15
    },
    {
        "name": "Cubicle Fruit",
        "description": "Fruta en forma de cubo que nutre bien.",
        "price": 15
    },
    {
        "name": "Heart Fruit",
        "description": "Aumenta felicidad y vínculo con el Chao.",
        "price": 60
    },
    {
        "name": "Chao Fruit",
        "description": "Fruta especial que mejora todas las estadísticas.",
        "price": 80
    },
    {
        "name": "Mushroom",
        "description": "Un champiñón extraño, muy nutritivo.",
        "price": 30
    },
    {
        "name": "Strong Fruit",
        "description": "Mejora stamina y poder al comerla.",
        "price": 40
    },
    {
        "name": "Tasty Fruit",
        "description": "Fruta deliciosa que aumenta la felicidad.",
        "price": 20
    }
]

SOMBREROS_ITEMS = [
    {"name": "Calabaza", "description": "¡Asusta a tus amigos con este casco vegetal!", "price": 15},
    {"name": "Calavera", "description": "Ideal si quieres parecer un Chao fantasma.", "price": 15},
    {"name": "Gorro rojo de lana", "description": "Rojo intenso. Advertencia: no lava bien con ropa blanca.", "price": 10},
    {"name": "Gorro azul de lana", "description": "Perfecto para cuando tu Chao se cree un héroe polar.", "price": 10},
    {"name": "Gorro negro de lana", "description": "Para un look de Chao misterioso y elegante.", "price": 10},
    {"name": "Chupete", "description": "¡Porque tu Chao nunca dejará de ser un bebé!", "price": 5},
    {"name": "Cáscara de huevo normal", "description": "¿Recuerdas de dónde saliste? Ahora en tu cabeza.", "price": 5},
    {"name": "Balde", "description": "Cuando no hay casco, cualquier cubo sirve.", "price": 8},
    {"name": "Lata vacía", "description": "Hace cling-clang a cada paso. Diversión garantizada.", "price": 6},
    {"name": "Caja de cartón", "description": "Modo sigilo activado. ¡Que nadie te vea!", "price": 12},
    {"name": "Maceta", "description": "Por si tu Chao quiere florecer literalmente.", "price": 9},
    {"name": "Bolsa de papel", "description": "Para esos días de mucha vergüenza.", "price": 7},
    {"name": "Sartén", "description": "Protege tu cabeza y fríe un huevo si hace falta.", "price": 11},
    {"name": "Tocón", "description": "Para sentirte uno con la naturaleza (o casi).", "price": 13},
    {"name": "Sandía", "description": "Rica, fresca y algo pegajosa. ¡Atrévete!", "price": 14}
]

TOYS_ITEMS = [
    {"name": "Pala", "description": "Para que tu Chao cave agujeros donde no debe.", "price": 10},
    {"name": "Regadera", "description": "¡A mojar todo, incluso al vecino!", "price": 10},
    {"name": "Sonajero", "description": "Ideal para hacer ruido todo el día.", "price": 8},
    {"name": "Auto de juguete", "description": "Vrum vrum... ¡Carreras en miniatura!", "price": 12},
    {"name": "Muñeco de Sonic", "description": "¡Un héroe azul de peluche para abrazar!", "price": 14},
    {"name": "Escoba mágica", "description": "Para volar... o barrer tu desastre.", "price": 11},
    {"name": "Libro de dibujos", "description": "Historias que tu Chao no puede leer pero ama mirar.", "price": 9},
    {"name": "Saltador", "description": "¡Boing, boing! A rebotar por el jardín.", "price": 13},
    {"name": "Crayones", "description": "Para redecorar las paredes sin permiso.", "price": 7},
    {"name": "Varita de burbujas", "description": "Burbujas infinitas... hasta que se acabe el jabón.", "price": 10}
]

INSTRUMENTS_ITEMS = [
    {"name": "Campana", "description": "¡Ding ding! Hora de molestar a todos.", "price": 10},
    {"name": "Castañuelas", "description": "Tac tac tac... ritmo sin control.", "price": 9},
    {"name": "Platillos", "description": "CLANG. Perfecto para despertar a medio mundo.", "price": 12},
    {"name": "Tambor", "description": "Boom boom... que tiemble el jardín.", "price": 13},
    {"name": "Flauta", "description": "Melodías que a veces suenan bien.", "price": 11},
    {"name": "Maracas", "description": "Shake shake... y sacude el aburrimiento.", "price": 10},
    {"name": "Trompeta", "description": "¡Prrr! Una nota alta que rompe oídos.", "price": 12},
    {"name": "Pandereta", "description": "Tintineo alegre, ideal para fiestas improvisadas.", "price": 11}
]

chao_data = {}

# ==========================
# Comandos de crianza y cuidado con imágenes
# ==========================

@bot.command()
async def adoptar(ctx, nombre: str, color: str = "comun"):
    """Adopta un nuevo Chao"""
    user_id = str(ctx.author.id)
    if user_id in chaos_data:
        embed = discord.Embed(
            description="❌ ¡Ya tienes un Chao!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if color.lower() == "comun":
        color = "Azul Claro (Neutral)"

    chaos_data[user_id] = {
        "name": nombre,
        "level": 1,
        "hunger": 50,
        "happiness": 0,
        "type": "Normal",
        "image": CHAO_IMAGES["Normal"],
        "owner_id": user_id,
        "stage": "egg",
        "swim": 0,
        "fly": 0,
        "run": 0,
        "power": 0,
        "stamina": 0,
        "swim_level": 0,
        "fly_level": 0,
        "run_level": 0,
        "power_level": 0,
        "stamina_level": 0,
        "color": color.capitalize(),
        "outfit": "Ninguno",
        "alignment": 0,
        "inventory": {},
        "magnitude": {
            "swim": 0,
            "fly": 0,
            "run": 0,
            "power": 0
        },
        "rebirths": 0,
        "animales_inventario": [],
        "partes": [],
        "last_meal": datetime.datetime.utcnow().isoformat()
    }

    guardar_chaos()

    embed = discord.Embed(
        title="🌱 Nuevo huevo adoptado",
        description=(
            f"Has adoptado un huevo llamado **{nombre}** de color **{color.capitalize()}**.\n\n"
            "Para que nazca, puedes usar:\n"
            "🥚 `$sacudir` - Sacudirlo suavemente.\n"
            "🎵 `$silbar` - Ayudarle a nacer con tu silbido.\n"
            "💞 `$acariciar` - Hacerlo sentir más cálido.\n"
            "💥 `$lanzar` - Romper el cascarón de forma brusca."
        ),
        color=discord.Color.green()
    )
    file = discord.File("images/adopcion.png", filename="adopcion.png")
    embed.set_image(url="attachment://adopcion.png")
    await ctx.send(embed=embed, file=file)

@bot.command()
async def sacudir(ctx):
    """Sacude el huevo o divierte a tu Chao si ya nació"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un huevo ni un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    actualizar_hambre(user_id)

    if chao["stage"] == "egg":
        embed = discord.Embed(
            title="🥚 Huevo sacudido",
            description="El huevo se movió suavemente. Puedes `$acariciar` o `$silbar` para que nazca.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    else:
        chao["happiness"] = min(100, chao["happiness"] + 3)
        guardar_chaos()
        embed = discord.Embed(
            title="✨ Tiempo de juego",
            description=f"Has sacudido a **{chao['name']}** y se divirtió.\n😊 Felicidad: {chao['happiness']}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

@bot.command()
async def acariciar(ctx):
    """Acaricia el huevo o al Chao"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    actualizar_hambre(user_id)

    if chao["stage"] == "egg":
        embed = discord.Embed(
            title="💞 Acaricias el huevo",
            description="El huevo se siente más cálido. Puedes `$silbar` para ayudarle a nacer.",
            color=discord.Color.pink()
        )
        await ctx.send(embed=embed)
    else:
        chao["happiness"] = min(100, chao["happiness"] + 5)
        guardar_chaos()
        embed = discord.Embed(
            title="💖 Acariciaste a tu Chao",
            description=f"**{chao['name']}** está más feliz.\nFelicidad: {chao['happiness']}",
            color=discord.Color.pink()
        )
        await ctx.send(embed=embed)

@bot.command()
async def silbar(ctx):
    """Silba para que el huevo nazca o el Chao venga a ti"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    actualizar_hambre(user_id)

    if chao["stage"] == "egg":
        chao["stage"] = "child"
        chao["happiness"] = 30
        guardar_chaos()
        embed = discord.Embed(
            title="🎵 Silbido mágico",
            description=f"El huevo se abrió y nació **{chao['name']}**.\n¡Felicidades!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        chao["happiness"] = min(100, chao["happiness"] + 3)
        guardar_chaos()
        embed = discord.Embed(
            title="🐾 Tu Chao vino hacia ti",
            description=f"**{chao['name']}** se acercó felizmente.\nFelicidad: {chao['happiness']}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

@bot.command()
async def lanzar(ctx):
    """Lanza el huevo para que nazca o maltrata al Chao"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    actualizar_hambre(user_id)

    if chao["stage"] == "egg":
        chao["stage"] = "child"
        chao["happiness"] = -30
        guardar_chaos()
        embed = discord.Embed(
            title="💥 Nacimiento brusco",
            description=(
                f"Has lanzado el huevo. **{chao['name']}** nació muy asustado.\n"
                "Felicidad inicial: -30."
            ),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        chao["happiness"] = max(-100, chao["happiness"] - 20)
        guardar_chaos()
        embed = discord.Embed(
            title="😠 Maltrato",
            description=f"Has lanzado a **{chao['name']}**. Se siente muy mal.\nFelicidad: {chao['happiness']}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def golpear(ctx):
    """Golpea al Chao para bajarle felicidad y alineación"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    actualizar_hambre(user_id)

    chao["happiness"] = max(-100, chao["happiness"] - 25)
    chao["alignment"] = max(-1000, chao["alignment"] - 50)
    guardar_chaos()
    embed = discord.Embed(
        title="💢 Has golpeado a tu Chao",
        description=(
            f"**{chao['name']}** se siente herido y triste.\n"
            f"Felicidad: {chao['happiness']} | Alineación: {chao['alignment']}"
        ),
        color=discord.Color.dark_red()
    )
    await ctx.send(embed=embed)

@bot.command()
async def regañar(ctx):
    """Regaña a tu Chao, baja un poco la felicidad"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    chao["happiness"] = max(-100, chao["happiness"] - 10)
    guardar_chaos()
    embed = discord.Embed(
        description=f"🙁 Has regañado a **{chao['name']}**. Felicidad actual: **{chao['happiness']}**",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

@bot.command()
async def ignorar(ctx):
    """Ignora a tu Chao, baja más felicidad"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    chao["happiness"] = max(-100, chao["happiness"] - 20)
    guardar_chaos()
    embed = discord.Embed(
        description=f"😢 Has ignorado a **{chao['name']}** durante un tiempo. Se siente muy triste.\nFelicidad actual: **{chao['happiness']}**",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
async def mi_chao(ctx):
    """Muestra información detallada y decorativa del Chao"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao todavía.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]

    embed = discord.Embed(
        title=f"╭・꒰`🍒` {chao['name']}︶꒷꒥",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=chao["image"])
    embed.set_image(url="attachment://mi_chao.jpg")

    embed.description = (
        f"│・`🎭`**Etapa:** {chao['stage']}\n"
        f"│・`🐹`**Tipo:** {chao['type']}\n"
        f"│・`🌈`**Color:** {chao['color']}\n"
        f"│・`🕶`**Atuendo:** {chao.get('outfit', 'Ninguno')}\n"
        f"│・`🎚️`**Nivel:** {chao['level']}\n"
        f"│・`🍉`**Hambre:** {chao['hunger']}\n"
        f"╰・꒰`😁`**Felicidad:** {chao['happiness']}︶꒷꒥\n\n"
        f"✧╭･ﾟ꒰`📊`꒱﹕**Estadísticas:**\n"
        f"✧│･ﾟ`🥽` Swim: {chao['swim']}   `🪂` Fly: {chao['fly']}\n"
        f"✧│･ﾟ`🎽` Run: {chao['run']}   `💪` Power: {chao['power']}\n"
        f"✧│･ﾟ`🔰` Stamina: {chao['stamina']}\n"
        f"✧╰･ﾟ꒰`🧬`꒱﹕**Alineación:** {chao['alignment']}"
    )

    file = discord.File("images/mi_chao.jpg", filename="mi_chao.jpg")
    await ctx.send(embed=embed, file=file)

class GoodbyeView(View):
    def __init__(self, user_id):
        super().__init__(timeout=30)
        self.user_id = user_id

    @button(label="✅ Sí, despedirme", style=discord.ButtonStyle.red)
    async def goodbye_confirm(self, interaction: discord.Interaction, button: Button):
        if self.user_id in chaos_data:
            nombre = chaos_data[self.user_id]["name"]
            del chaos_data[self.user_id]
            guardar_chaos()

            embed = discord.Embed(
                title="💔 Despedida final",
                description=(
                    f"**🌳 {nombre} tendrá una vida feliz en un bosque lejano.**\n\n"
                    "🕊️ Nunca volverás a ver a tu Chao."
                ),
                color=discord.Color.dark_red()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            file = discord.File("images/goodbye.png", filename="goodbye.png")
            embed.set_image(url="attachment://goodbye.png")

            await interaction.message.edit(embed=embed, attachments=[file], view=None)
        else:
            embed = discord.Embed(
                description="❌ No tienes un Chao para despedir.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @button(label="❌ Cancelar", style=discord.ButtonStyle.gray)
    async def goodbye_cancel(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="❎ Despedida cancelada",
            description="Tu Chao seguirá contigo.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        file = discord.File("images/goodbye.png", filename="goodbye.png")
        embed.set_image(url="attachment://goodbye.png")

        await interaction.message.edit(embed=embed, attachments=[file], view=None)

@bot.command()
async def goodbye(ctx):
    """Despedirte de tu Chao para siempre"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao para despedir.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    nombre = chaos_data[user_id]["name"]
    embed = discord.Embed(
        title="👋 ¿Estás seguro de que quieres despedirte?",
        description=(
            f"Estás por abandonar a **{nombre}**.\n"
            "Esta acción es **permanente**.\n\n"
            "¿Estás realmente seguro?"
        ),
        color=discord.Color.orange()
    )
    # Thumbnail con el avatar del autor
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    # Imagen central
    file = discord.File("images/goodbye.png", filename="goodbye.png")
    embed.set_image(url="attachment://goodbye.png")

    view = GoodbyeView(user_id)
    await ctx.send(embed=embed, file=file, view=view)

# ==========================
# Entrenamiento de atributos
# ==========================

async def entrenar(ctx, atributo):
    """Entrena un atributo específico"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    puntos = random.randint(1, 3)
    chao[atributo] += puntos
    chao["happiness"] = min(100, chao["happiness"] + 2)
    chao["hunger"] = min(100, chao["hunger"] + 2)  # sube el hambre por esfuerzo

    guardar_chaos()

    embed = discord.Embed(
        title="🏋️ Entrenamiento",
        description=(
            f"**{chao['name']}** entrenó **{atributo.capitalize()}**.\n"
            f"🔹 +{puntos} puntos.\n"
            f"❤️ Felicidad: {chao['happiness']}\n"
            f"🍽️ Hambre: {chao['hunger']}"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def entrenar_swim(ctx):
    await entrenar(ctx, "swim")

@bot.command()
async def entrenar_fly(ctx):
    await entrenar(ctx, "fly")

@bot.command()
async def entrenar_run(ctx):
    await entrenar(ctx, "run")

@bot.command()
async def entrenar_power(ctx):
    await entrenar(ctx, "power")

@bot.command()
async def alimentar(ctx, *, fruta: str):
    """Alimenta a tu Chao con una fruta del inventario"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]
    inventario = chao.get("inventory", {})
    fruta_input = fruta.strip().lower()

    # Buscar fruta real en MEAL_ITEMS
    fruta_real = next((item for item in MEAL_ITEMS if item["name"].lower() == fruta_input), None)
    if not fruta_real:
        embed = discord.Embed(
            description="❌ Fruta no válida. Usa `$shop_meal` para ver las disponibles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Comprobar si está en inventario usando búsqueda flexible
    matching_key = next((k for k in inventario.keys() if k.lower() == fruta_input), None)
    if not matching_key:
        embed = discord.Embed(
            description=f"❌ No tienes **{fruta_real['name']}** en tu inventario.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Efectos según la fruta
    efectos = {
        "regular fruit":      {"hunger": 15, "stamina": 1, "happiness": 0},
        "hero fruit":         {"alignment": 100, "hunger": 10, "happiness": 5},
        "dark fruit":         {"alignment": -100, "hunger": 10, "happiness": -5},
        "round fruit":        {"hunger": 20, "stamina": 1},
        "triangular fruit":   {"hunger": 20, "happiness": 3},
        "cubicle fruit":      {"hunger": 20, "stamina": 1},
        "heart fruit":        {"happiness": 15, "hunger": 10},
        "chao fruit":         {"hunger": 15, "stamina": 2, "happiness": 5, "power": 1, "fly": 1, "run": 1, "swim": 1},
        "mushroom":           {"hunger": 25, "stamina": 2},
        "strong fruit":       {"stamina": 3, "power": 2},
        "tasty fruit":        {"hunger": 10, "happiness": 10}
    }

    efecto = efectos.get(fruta_real["name"].lower(), {})
    chao["hunger"] = max(0, chao.get("hunger", 0) - efecto.get("hunger", 0))
    chao["stamina"] = min(10, chao.get("stamina", 0) + efecto.get("stamina", 0))
    chao["happiness"] = max(-100, min(100, chao.get("happiness", 0) + efecto.get("happiness", 0)))
    chao["alignment"] = max(-1000, min(1000, chao.get("alignment", 0) + efecto.get("alignment", 0)))
    for stat in ["power", "swim", "fly", "run"]:
        chao[stat] = chao.get(stat, 0) + efecto.get(stat, 0)

    # Consumir fruta
    inventario[matching_key] -= 1
    if inventario[matching_key] <= 0:
        del inventario[matching_key]

    guardar_chaos()

    # Resumen visual
    efecto_texto = []
    if "hunger" in efecto:    efecto_texto.append(f"🍉 Hambre -{efecto['hunger']}")
    if "stamina" in efecto:   efecto_texto.append(f"💪 Stamina +{efecto['stamina']}")
    if "happiness" in efecto: efecto_texto.append(f"😁 Felicidad {'+' if efecto['happiness'] >= 0 else ''}{efecto['happiness']}")
    if "alignment" in efecto:
        alineacion = "Hero" if efecto["alignment"] > 0 else "Dark"
        efecto_texto.append(f"🌟 Alineación: {alineacion}")
    for stat in ["power", "swim", "fly", "run"]:
        if stat in efecto:
            emoji = {
                "power": "💪", "swim": "🥽", "fly": "🪂", "run": "🎽"
            }[stat]
            efecto_texto.append(f"{emoji} {stat.capitalize()} +{efecto[stat]}")

    embed = discord.Embed(
        title=f"🍽️ {chao['name']} fue alimentado con {fruta_real['name']}",
        description="\n".join(efecto_texto),
        color=discord.Color.green()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1352064925828124693/1394514208250531940/alimentar.webp?ex=68771610&is=6875c490&hm=8623eaabd4659549dc39226d60d49589dfd9b1fdbdfd44dfc873d70691f324cf&")  # Cambia esto si usas una URL distinta
    await ctx.send(embed=embed)

# ==========================
# Acciones o Usar
# ==========================

@bot.command()
async def usar_juguete(ctx, *, juguete: str):
    """Usar un juguete con opciones interactivas"""
    user_id = str(ctx.author.id)
    chao = chaos_data.get(user_id)
    if not chao:
        await ctx.send(embed=discord.Embed(description="❌ No tienes un Chao.", color=discord.Color.red()))
        return

    juguetes = chao.setdefault("juguetes", [])
    # Normalizar entrada
    juguete_input = juguete.strip().lower()

    # Buscar con tolerancia
    matching = [j for j in juguetes if j.strip().lower() == juguete_input]
    if not matching:
        await ctx.send(embed=discord.Embed(description=f"❌ No tienes el juguete: **{juguete}**.", color=discord.Color.red()))
        return

    juguetes.remove(matching[0])
    guardar_chaos()

    embed = discord.Embed(
        title=f"🧸 Jugando con {matching[0]}",
        description="¿Qué quieres hacer?",
        color=discord.Color.orange()
    )
    embed.add_field(
        name="Opciones",
        value="🔵 *Jugar suavemente*\n🟢 *Lanzar al aire*\n🔴 *Esconderlo*",
        inline=False
    )
    view = UsarJugueteView(ctx.author.id, matching[0])
    await ctx.send(embed=embed, view=view)

class UsarJugueteView(View):
    def __init__(self, user_id, juguete):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.juguete = juguete

    @discord.ui.button(label="🔵 Suavemente", style=discord.ButtonStyle.primary)
    async def suave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.recompensa(interaction, 5)

    @discord.ui.button(label="🟢 Lanzar", style=discord.ButtonStyle.success)
    async def lanzar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.recompensa(interaction, 3)

    @discord.ui.button(label="🔴 Esconder", style=discord.ButtonStyle.danger)
    async def esconder(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.recompensa(interaction, 2)

    async def recompensa(self, interaction, felicidad):
        user_id = str(interaction.user.id)
        if user_id != self.user_id:
            await interaction.response.send_message("❌ Este juguete no es tuyo.", ephemeral=True)
            return

        chao = chaos_data.get(user_id)
        chao["happiness"] = min(100, chao.get("happiness", 0) + felicidad)
        guardar_chaos()

        embed = discord.Embed(
            description=f"🎉 Tu Chao jugó con **{self.juguete}**.\nFelicidad +{felicidad} ❤️",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)

@bot.command()
async def tocar_instrumento(ctx, *, instrumento: str):
    """Tocar un instrumento con modos de juego"""
    user_id = str(ctx.author.id)
    chao = chaos_data.get(user_id)
    if not chao:
        await ctx.send(embed=discord.Embed(description="❌ No tienes un Chao.", color=discord.Color.red()))
        return

    instrumentos = chao.setdefault("instrumentos", [])
    instrumento_input = instrumento.strip().lower()

    matching = [i for i in instrumentos if i.strip().lower() == instrumento_input]
    if not matching:
        await ctx.send(embed=discord.Embed(description=f"❌ No tienes el instrumento: **{instrumento}**.", color=discord.Color.red()))
        return

    embed = discord.Embed(
        title=f"🎵 Tocando {matching[0]}",
        description="Elige un modo de juego para interactuar:",
        color=discord.Color.blue()
    )
    view = TocarInstrumentoModoView(str(ctx.author.id), matching[0])
    await ctx.send(embed=embed, view=view)

class TocarInstrumentoModoView(View):
    def __init__(self, user_id, instrumento):
        super().__init__(timeout=30)
        self.user_id = str(user_id)
        self.instrumento = instrumento

    @discord.ui.button(label="🟢 Libre", style=discord.ButtonStyle.success)
    async def libre(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description="🎵 Modo Libre:\nToca 4 notas como quieras.",
            color=discord.Color.green()
        )
        view = TocarLibreView(str(interaction.user.id), self.instrumento)
        message = await interaction.response.edit_message(embed=embed, view=view)
        view.message = message

    @discord.ui.button(label="🟡 Secuencia", style=discord.ButtonStyle.secondary)
    async def secuencia(self, interaction: discord.Interaction, button: discord.ui.Button):
        secuencia = ["🔴", "🟢", "🔵"]
        embed = discord.Embed(
            description=f"🟡 Modo Secuencia:\nSigue esta secuencia:\n{' '.join(secuencia)}",
            color=discord.Color.yellow()
        )
        view = TocarSecuenciaView(str(interaction.user.id), self.instrumento, secuencia)
        message = await interaction.response.edit_message(embed=embed, view=view)
        view.message = message

    @discord.ui.button(label="🔵 Aleatorio", style=discord.ButtonStyle.primary)
    async def aleatorio(self, interaction: discord.Interaction, button: discord.ui.Button):
        aleatorio = [random.choice(["🔴", "🟢", "🔵"]) for _ in range(3)]
        embed = discord.Embed(
            description=f"🔵 Modo Aleatorio:\nRepite esta secuencia:\n{' '.join(aleatorio)}",
            color=discord.Color.blurple()
        )
        view = TocarAleatorioView(str(interaction.user.id), self.instrumento, aleatorio)
        message = await interaction.response.edit_message(embed=embed, view=view)
        view.message = message

# MODO LIBRE
class TocarLibreView(View):
    def __init__(self, user_id, instrumento):
        super().__init__(timeout=60)
        self.user_id = str(user_id)
        self.instrumento = instrumento
        self.notas = []
        self.message = None

    async def actualizar_embed(self, interaction):
        notas_texto = " ".join(self.notas) if self.notas else "*Ninguna nota tocada aún*"
        embed = discord.Embed(
            title=f"🎶 Tocando libremente el {self.instrumento}",
            description=f"Notas tocadas: {notas_texto}",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔴", style=discord.ButtonStyle.danger)
    async def nota_roja(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            return
        self.notas.append("🔴")
        await self.actualizar_embed(interaction)

    @discord.ui.button(label="🟢", style=discord.ButtonStyle.success)
    async def nota_verde(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            return
        self.notas.append("🟢")
        await self.actualizar_embed(interaction)

    @discord.ui.button(label="🔵", style=discord.ButtonStyle.primary)
    async def nota_azul(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            return
        self.notas.append("🔵")
        await self.actualizar_embed(interaction)

# MODO SECUENCIA
class TocarSecuenciaView(View):
    def __init__(self, user_id, instrumento, secuencia=None):
        super().__init__(timeout=60)
        self.user_id = str(user_id)
        self.instrumento = instrumento
        self.progreso = []
        self.secuencia = secuencia if secuencia else self.generar_secuencia(4)
        self.message = None

    def generar_secuencia(self, longitud):
        return [random.choice(["🔴", "🟢", "🔵"]) for _ in range(longitud)]

    def mostrar_progreso(self):
        resultado = []
        for i, nota in enumerate(self.secuencia):
            if i < len(self.progreso):
                resultado.append("✅")
            else:
                resultado.append(nota)
        return " ".join(resultado)

    async def actualizar_embed(self, interaction, mensaje=None, color=discord.Color.yellow()):
        texto = (
            f"🟡 **Modo Secuencia**\n"
            f"Repite esta secuencia:\n{self.mostrar_progreso()}\n\n"
            f"{mensaje if mensaje else ''}"
        )
        embed = discord.Embed(description=texto, color=color)
        await interaction.response.edit_message(embed=embed, view=self)

    async def verificar(self, interaction, nota):
        if str(interaction.user.id) != self.user_id:
            return

        esperada = self.secuencia[len(self.progreso)]
        if nota == esperada:
            self.progreso.append(nota)
            if len(self.progreso) == len(self.secuencia):
                longitud_nueva = min(len(self.secuencia) + 2, 8)
                self.secuencia = self.generar_secuencia(longitud_nueva)
                self.progreso = []
                await self.actualizar_embed(interaction, mensaje="✅ ¡Secuencia completada! Nueva secuencia generada.", color=discord.Color.green())
            else:
                await self.actualizar_embed(interaction)
        else:
            self.progreso = []
            await self.actualizar_embed(interaction, mensaje="❌ Te equivocaste. La secuencia se reinicia.", color=discord.Color.red())

    @discord.ui.button(label="🔴", style=discord.ButtonStyle.danger)
    async def roja(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.verificar(interaction, "🔴")

    @discord.ui.button(label="🟢", style=discord.ButtonStyle.success)
    async def verde(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.verificar(interaction, "🟢")

    @discord.ui.button(label="🔵", style=discord.ButtonStyle.primary)
    async def azul(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.verificar(interaction, "🔵")

# MODO ALEATORIO
class TocarAleatorioView(View):
    def __init__(self, user_id, instrumento, secuencia):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.instrumento = instrumento
        self.secuencia = secuencia
        self.indice = 0
        self.progreso = []

    def generar_secuencia(self, longitud):
        return [random.choice(["🔴", "🟢", "🔵"]) for _ in range(longitud)]

    def mostrar_progreso(self):
        resultado = []
        for i, nota in enumerate(self.secuencia):
            if i < len(self.progreso):
                resultado.append("✅")
            else:
                resultado.append("❓")
        return " ".join(resultado)

    async def actualizar_embed(self, interaction, mensaje=None, color=discord.Color.blurple()):
        embed = discord.Embed(
            title=f"🔵 Modo Aleatorio - {self.instrumento}",
            description=f"Repite esta secuencia aleatoria:\n{self.mostrar_progreso()}\n\n{mensaje if mensaje else ''}",
            color=color
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def verificar(self, interaction, nota):
        if str(interaction.user.id) != self.user_id:
            return

        esperada = self.secuencia[len(self.progreso)]
        if nota == esperada:
            self.progreso.append(nota)
            if len(self.progreso) == len(self.secuencia):
                self.secuencia = self.generar_secuencia(5)
                self.progreso = []
                await self.actualizar_embed(interaction, mensaje="✅ ¡Secuencia completada! Nueva generada.", color=discord.Color.green())
            else:
                await self.actualizar_embed(interaction)
        else:
            self.progreso = []
            await self.actualizar_embed(interaction, mensaje="❌ Fallaste. La secuencia cambia.", color=discord.Color.red())

    @discord.ui.button(label="🔴", style=discord.ButtonStyle.danger)
    async def rojo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.verificar(interaction, "🔴")

    @discord.ui.button(label="🟢", style=discord.ButtonStyle.success)
    async def verde(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.verificar(interaction, "🟢")

    @discord.ui.button(label="🔵", style=discord.ButtonStyle.primary)
    async def azul(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.verificar(interaction, "🔵")

# ==========================
# Evolución (botón de confirmación)
# ==========================

@bot.command()
async def evolucionar(ctx):
    """Permite evolucionar tu Chao si cumple los requisitos"""
    user_id = str(ctx.author.id)
    if user_id not in chaos_data:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    chao = chaos_data[user_id]

    if chao["stage"] != "child":
        embed = discord.Embed(
            description="⚠️ Tu Chao ya está evolucionado.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    # Revisar si alguna estadística llegó al nivel 10
    niveles = {
        "swim": chao.get("swim", 0),
        "fly": chao.get("fly", 0),
        "run": chao.get("run", 0),
        "power": chao.get("power", 0)
    }

    if all(valor < 10 for valor in niveles.values()):
        embed = discord.Embed(
            description=(
                "❌ Tu Chao necesita al menos una estadística en **10** para evolucionar.\n\n"
                "🏋️ Usa los comandos de entrenamiento:\n"
                "`$dar_swim`, `$dar_fly`, `$dar_run`, `$dar_power`."
            ),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="🌱 Evolución Disponible",
        description=(
            "**Tu Chao está listo para evolucionar.**\n\n"
            "Pulsa el botón si deseas evolucionar ahora.\n\n"
            "📊 Estadísticas actuales:\n"
            f"🥽 Swim: **{niveles['swim']}/10**\n"
            f"🪂 Fly: **{niveles['fly']}/10**\n"
            f"🎽 Run: **{niveles['run']}/10**\n"
            f"💪 Power: **{niveles['power']}/10**"
        ),
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    view = EvolucionarView(user_id)
    await ctx.send(embed=embed, view=view)


class EvolucionarView(View):
    def __init__(self, user_id):
        super().__init__(timeout=30)
        self.user_id = user_id

    @button(label="✅ Evolucionar", style=discord.ButtonStyle.green)
    async def confirmar(self, interaction: discord.Interaction, button: Button):
        chao = chaos_data.get(self.user_id)
        if not chao:
            await interaction.response.send_message(
                "❌ No se encontró tu Chao.",
                ephemeral=True
            )
            return

        # Determinar la estadística principal
        niveles = {
            "swim": chao.get("swim", 0),
            "fly": chao.get("fly", 0),
            "run": chao.get("run", 0),
            "power": chao.get("power", 0)
        }
        atributo_mayor = max(niveles, key=niveles.get)

        # Determinar alineación
        alignment = chao.get("alignment", 0)
        if alignment >= 500:
            alineacion = "hero"
        elif alignment <= -500:
            alineacion = "dark"
        else:
            alineacion = "neutral"

        etapa = f"adult {alineacion} {atributo_mayor}"
        chao["type"] = atributo_mayor.capitalize()
        chao["stage"] = etapa
        chao["image"] = CHAO_IMAGES.get(alineacion.capitalize(), CHAO_IMAGES["Normal"])

        guardar_chaos()

        embed = discord.Embed(
            title="✨ Evolución completada",
            description=(
                f"🎉 **{chao['name']}** ha evolucionado a **{etapa.capitalize()}**.\n\n"
                f"💪 Estadística principal: **{atributo_mayor.capitalize()}**\n"
                f"🌈 Alineación: **{alineacion.capitalize()}**"
            ),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.message.edit(embed=embed, view=None)

    @button(label="❌ Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            description="❎ Evolución cancelada.",
            color=discord.Color.greyple()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.message.edit(embed=embed, view=None)

# ==========================
# Comandos de tiendas y economía
# ==========================

@bot.command()
async def shop_meal(ctx):
    """Muestra la tienda de frutas"""
    embed = discord.Embed(
        title="🍉 Tienda de Frutas",
        description="Compra frutas nutritivas para alimentar a tu Chao.",
        color=discord.Color.green()
    )
    for item in MEAL_ITEMS:
        embed.add_field(
            name=f"{item['name']} – {item['price']} 🪙",
            value=item['description'],
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def shop_outfits(ctx):
    """Muestra la tienda de atuendos"""
    embed = discord.Embed(
        title="🎩 Tienda de Atuendos",
        description="Personaliza a tu Chao con estos atuendos.",
        color=discord.Color.purple()
    )
    for item in SOMBREROS_ITEMS:
        embed.add_field(
            name=f"{item['name']} – {item['price']} 🪙",
            value=item['description'],
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def blackmarket(ctx):
    """Muestra el mercado negro"""
    embed = discord.Embed(
        title="🕶 Mercado Negro",
        description="Artículos raros y misteriosos.",
        color=discord.Color.dark_grey()
    )
    for item in BLACKMARKET_ITEMS:
        embed.add_field(
            name=f"{item['name']} – {item['price']} 🪙",
            value=item['description'],
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def shop_toys(ctx):
    """Muestra los juguetes disponibles para Chaos"""
    embed = discord.Embed(
        title="🧸 Tienda de Juguetes",
        description="Compra juguetes para entretener a tu Chao.",
        color=discord.Color.orange()
    )
    for item in TOYS_ITEMS:
        embed.add_field(
            name=f"{item['name']} - {item['price']} 🪙",
            value=item['description'],
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def shop_tools(ctx):
    """Muestra los instrumentos disponibles para Chaos músicos"""
    embed = discord.Embed(
        title="🎵 Tienda de Instrumentos",
        description="¡Haz que tu Chao cree su banda musical!",
        color=discord.Color.purple()
    )
    for item in INSTRUMENTS_ITEMS:
        embed.add_field(
            name=f"{item['name']} - {item['price']} 🪙",
            value=item['description'],
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def saldo(ctx):
    """Muestra tu saldo actual"""
    user_id = str(ctx.author.id)
    coins = economy.get(user_id, 0)
    await ctx.send(f"💰 Tu saldo actual es: **{coins}** monedas.")

class CarreraView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.pulsaciones = 0
        self.message = None  # Para poder acceder al mensaje más adelante

    @discord.ui.button(label="🏃 Correr", style=discord.ButtonStyle.green)
    async def correr(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Solo tú puedes usar este botón.", ephemeral=True)
            return

        self.pulsaciones += 1
        if self.pulsaciones >= 25:
            economy[self.user_id] = economy.get(self.user_id, 0) + 60
            guardar_economy()

            embed = discord.Embed(
                title="🏁 ¡Carrera completada!",
                description="🥇 ¡Llegaste a la meta!\nRecibiste **60 monedas**. 🪙",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                description=f"🏃 Pulsaciones: **{self.pulsaciones}/25**",
                color=discord.Color.blurple()
            )
            await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        if self.pulsaciones == 0:
            return  # Si no hizo nada, no mandamos mensaje

        coins_ganadas = self.pulsaciones * 2
        economy[self.user_id] = economy.get(self.user_id, 0) + coins_ganadas
        guardar_economy()

        if self.message:
            canal = self.message.channel
            await canal.send(
                embed=discord.Embed(
                    title="⏱️ Tiempo agotado",
                    description=f"🏃 Pulsaciones totales: **{self.pulsaciones}**\nGanaste **{coins_ganadas} monedas**.",
                    color=discord.Color.orange()
                )
            )

@bot.command()
async def carrera(ctx):
    """Participa en una carrera presionando el botón rápidamente"""
    user_id = str(ctx.author.id)

    embed = discord.Embed(
        title="🏃 Carrera de Resistencia",
        description=(
            "Presiona el botón tantas veces como puedas en **60 segundos**.\n"
            "👉 Si llegas a **25 pulsaciones**, ganas **60 monedas**.\n"
            "👉 Si no llegas, ganas **2 monedas por pulsación**.\n\n"
            "¡Demuéstralo ahora!"
        ),
        color=discord.Color.green()
    )

    view = CarreraView(user_id)
    message = await ctx.send(embed=embed, view=view)
    view.message = message

@bot.command()
async def reclamar_diario(ctx):
    """Reclama recompensa diaria"""
    user_id = str(ctx.author.id)
    ahora = datetime.utcnow()
    ultima = last_claim.get(user_id)

    if ultima:
        ultima_fecha = datetime.fromisoformat(ultima)
        diferencia = (ahora - ultima_fecha).total_seconds()
        if diferencia < 86400:
            restante = 86400 - diferencia
            horas = int(restante // 3600)
            minutos = int((restante % 3600) // 60)
            await ctx.send(f"⏳ Ya reclamaste hoy. Intenta de nuevo en {horas}h {minutos}m.")
            return

    monedas = 50
    economy[user_id] = economy.get(user_id, 0) + monedas
    last_claim[user_id] = ahora.isoformat()
    guardar_economy()
    guardar_last_claim()
    await ctx.send(f"🌟 Reclamo diario exitoso. Recibiste **{monedas}** monedas.")

@bot.command()
async def comprar(ctx, item: str, cantidad: int = 1):
    """Compra frutas, atuendos, juguetes, instrumentos o items del mercado negro"""
    nombre = item.replace("_", " ").lower()
    user_id = str(ctx.author.id)
    saldo_actual = economy.get(user_id, 0)

    # Unificar todas las listas
    TODOS_LOS_ITEMS = MEAL_ITEMS + SOMBREROS_ITEMS + TOYS_ITEMS + INSTRUMENTS_ITEMS + BLACKMARKET_ITEMS

    producto = next((i for i in TODOS_LOS_ITEMS if i["name"].lower() == nombre), None)
    if not producto:
        embed = discord.Embed(
            description="❌ No existe ese objeto.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    precio_total = producto["price"] * cantidad
    if saldo_actual < precio_total:
        embed = discord.Embed(
            description="❌ No tienes suficiente dinero.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Descontar saldo
    economy[user_id] -= precio_total
    guardar_economy()

    # Añadir al inventario
    chao = chaos_data.get(user_id)
    if not chao:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Diferenciar tipo
    if producto in MEAL_ITEMS:
        inv = chao.setdefault("inventory", {})
        inv[nombre] = inv.get(nombre, 0) + cantidad
        categoria = "Fruta"
    elif producto in SOMBREROS_ITEMS:
        chao["outfit"] = producto["name"]
        categoria = "Atuendo (equipado)"
    elif producto in TOYS_ITEMS:
        juguetes = chao.setdefault("juguetes", [])
        juguetes.extend([producto["name"]] * cantidad)
        categoria = "Juguete"
    elif producto in INSTRUMENTS_ITEMS:
        instrumentos = chao.setdefault("instrumentos", [])
        instrumentos.extend([producto["name"]] * cantidad)
        categoria = "Instrumento"
    elif producto in BLACKMARKET_ITEMS:
        # Vamos a guardar Chaos Drives y objetos raros en un inventario especial
        black_inv = chao.setdefault("blackmarket_inventory", {})
        black_inv[nombre] = black_inv.get(nombre, 0) + cantidad
        categoria = "Mercado Negro"
    else:
        categoria = "Objeto"

    guardar_chaos()

    embed = discord.Embed(
        title="✅ Compra realizada",
        description=f"Has comprado **{cantidad} {producto['name']}** del {categoria}. ¡Que lo disfrutes! 🎉",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def inventario(ctx):
    """Muestra tu inventario con páginas por categoría"""
    user_id = str(ctx.author.id)
    chao = chaos_data.get(user_id)
    if not chao:
        embed = discord.Embed(
            description="❌ No tienes un Chao.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # ✅ Usar claves correctas
    inv_frutas = chao.get("inventory", {})
    juguetes = chao.get("juguetes", [])
    instrumentos = chao.get("instrumentos", [])
    atuendo = chao.get("outfit", "Ninguno")
    black_inv = chao.get("blackmarket_inventory", {})

    # Preparar los embeds de cada categoría
    embeds = []

    # Página 1 - Comida
    frutas_texto = "\n".join(f"- {k.capitalize()}: {v}" for k, v in inv_frutas.items()) if inv_frutas else "Vacío"
    embed1 = discord.Embed(
        title="🍏 Inventario: Frutas",
        description=frutas_texto,
        color=discord.Color.green()
    )
    embeds.append(embed1)

    # Página 2 - Ropa
    embed2 = discord.Embed(
        title="🎩 Inventario: Ropa",
        description=f"Atuendo equipado: **{atuendo}**",
        color=discord.Color.purple()
    )
    embeds.append(embed2)

    # Página 3 - Juguetes
    juguetes_texto = "\n".join(f"- {j}" for j in juguetes) if juguetes else "Vacío"
    embed3 = discord.Embed(
        title="🧸 Inventario: Juguetes",
        description=juguetes_texto,
        color=discord.Color.orange()
    )
    embeds.append(embed3)

    # Página 4 - Instrumentos
    instrumentos_texto = "\n".join(f"- {i}" for i in instrumentos) if instrumentos else "Vacío"
    embed4 = discord.Embed(
        title="🎵 Inventario: Instrumentos",
        description=instrumentos_texto,
        color=discord.Color.blue()
    )
    embeds.append(embed4)

    # Página 5 - Blackmarket
    black_texto = "\n".join(f"- {k.capitalize()}: {v}" for k, v in black_inv.items()) if black_inv else "Vacío"
    embed5 = discord.Embed(
        title="🕶 Inventario: Blackmarket",
        description=black_texto,
        color=discord.Color.dark_grey()
    )
    embeds.append(embed5)

    view = InventarioView(embeds)
    message = await ctx.send(embed=embeds[0], view=view)
    view.message = message


class InventarioView(View):
    def __init__(self, embeds):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.blurple)
    async def anterior(self, interaction: discord.Interaction, button: Button):
        self.current_page = (self.current_page - 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="➡️ Siguiente", style=discord.ButtonStyle.blurple)
    async def siguiente(self, interaction: discord.Interaction, button: Button):
        self.current_page = (self.current_page + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

# ==========================
# Datos de animales y partes
# ==========================

ANIMALES_PARTES = {
    "foca": ["brazos"],
    "pingüino": ["brazos"],
    "nutria": ["cola"],
    "pavo real": ["alas"],
    "golondrina": ["alas"],
    "loro": ["alas"],
    "ciervo": ["cuernos"],
    "conejo": ["piernas"],
    "canguro": ["piernas"],
    "gorila": ["brazos"],
    "león": ["cola"],
    "elefante": ["frente"],
    "topo": ["brazos"],
    "koala": ["orejas"],
    "mofeta": ["cola"],
    "cóndor": ["alas"],
    "guepardo": ["piernas"],
    "jabalí": ["cuernos"],
    "oso": ["brazos"],
    "tigre": ["piernas"],
    "oveja": ["cuernos"],
    "mapache": ["cola"],
    "pez mitad": ["cola"],
    "perro esqueleto": ["cola"],
    "murciélago": ["alas"],
    "dragón": ["cuernos", "cola", "alas"],
    "unicornio": ["cuernos"],
    "fénix": ["alas"]
}

@bot.command()
async def animales(ctx):
    """Muestra todos los animales disponibles"""
    embed = discord.Embed(
        title="🐾 Animales Disponibles",
        description="Animales que puedes comprar para que tu Chao adquiera rasgos únicos.",
        color=discord.Color.green()
    )

    texto = ""
    for animal, partes in ANIMALES_PARTES.items():
        texto += f"- **{animal.capitalize()}**: {', '.join(partes)}\n"

    embed.add_field(
        name="Lista de animales y partes",
        value=texto,
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def comprar_animales(ctx, animal: str):
    """Compra un animal"""
    animal = animal.lower()
    if animal not in ANIMALES_PARTES:
        await ctx.send("❌ Ese animal no existe. Usa `$animales` para ver la lista.")
        return

    user_id = str(ctx.author.id)
    chao = chaos_data.get(user_id)
    if not chao:
        await ctx.send("❌ No tienes un Chao.")
        return

    inventario = chao.setdefault("animales_inventario", [])
    inventario.append(animal)
    guardar_chaos()
    await ctx.send(f"✅ Compraste un **{animal.capitalize()}**. Ya está en tu inventario.")

@bot.command()
async def usar_animales(ctx, animal: str):
    """Usa un animal para que tu Chao obtenga sus partes"""
    animal = animal.lower()
    user_id = str(ctx.author.id)
    chao = chaos_data.get(user_id)

    if not chao:
        await ctx.send("❌ No tienes un Chao.")
        return

    inventario = chao.setdefault("animales_inventario", [])
    partes = chao.setdefault("partes", [])

    if animal not in inventario:
        await ctx.send("❌ No tienes ese animal en tu inventario.")
        return

    inventario.remove(animal)

    for parte in ANIMALES_PARTES[animal]:
        partes.append({"parte": parte, "animal": animal})

    guardar_chaos()
    await ctx.send(
        f"✨ Tu Chao absorbió un **{animal.capitalize()}** y ganó: {', '.join(ANIMALES_PARTES[animal])}."
    )

@bot.command()
async def estadisticas(ctx):
    """Muestra las partes adquiridas por el Chao"""
    user_id = str(ctx.author.id)
    chao = chaos_data.get(user_id)

    if not chao:
        await ctx.send("❌ No tienes un Chao.")
        return

    partes = chao.get("partes", [])
    inventario = chao.get("animales_inventario", [])

    if partes:
        texto_partes = ""
        for p in partes:
            parte = p.get("parte", "Desconocido")
            animal = p.get("animal", "Desconocido")
            texto_partes += f"- **{parte.capitalize()}** de {animal.capitalize()}\n"
    else:
        texto_partes = "Ninguna"

    embed = discord.Embed(
        title=f"📈 Estadísticas de {chao['name']}",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🐾 Partes de animales",
        value=texto_partes,
        inline=False
    )
    embed.add_field(
        name="🎒 Inventario de animales",
        value=", ".join(a.capitalize() for a in inventario) if inventario else "Vacío",
        inline=False
    )
    await ctx.send(embed=embed)

# ==========================
# Comando de guía de evolución
# ==========================

@bot.command()
async def guia(ctx):
    """Muestra la guía de evolución de los Chaos"""
    paginas = []

    # Página Neutral
    embed1 = discord.Embed(
        title="🌱 Evolución Neutral",
        description=(
            "Un Chao Neutral evoluciona si su alineación se mantiene equilibrada.\n\n"
            "**Requisitos:**\n"
            "- Alineación cercana a 0.\n"
            "- Entrenar cualquier estadística.\n\n"
            "**Resultado:**\n"
            "Evolución en forma Neutral con aspecto amistoso."
        ),
        color=discord.Color.green()
    )
    embed1.set_image(url="https://images.steamusercontent.com/ugc/547554879388440446/175041171CA1BF64968EC9E52BDDC01E3E9B60B1/")
    paginas.append(embed1)

    # Página Hero
    embed2 = discord.Embed(
        title="✨ Evolución Hero",
        description=(
            "Un Chao Hero evoluciona con alineación positiva.\n\n"
            "**Requisitos:**\n"
            "- Alineación mayor a +500.\n"
            "- Cuídalo bien y aliméntalo.\n\n"
            "**Resultado:**\n"
            "Evolución Hero de aspecto luminoso."
        ),
        color=discord.Color.blue()
    )
    embed2.set_image(url="https://static.wikia.nocookie.net/monster/images/2/2d/Hero_Evolution_Chao_Chart_by_ChaoGarden.png/revision/latest?cb=20170528233212")
    paginas.append(embed2)

    # Página Dark
    embed3 = discord.Embed(
        title="💀 Evolución Dark",
        description=(
            "Un Chao Dark evoluciona con alineación negativa.\n\n"
            "**Requisitos:**\n"
            "- Alineación menor a -500.\n"
            "- Trátalo de forma traviesa.\n\n"
            "**Resultado:**\n"
            "Evolución Dark de aspecto siniestro."
        ),
        color=discord.Color.dark_red()
    )
    embed3.set_image(url="https://static.wikia.nocookie.net/monster/images/c/ce/Dark_evolution_chao_chart_by_v1ciouz_mizz_azn-d342ow1.png/revision/latest?cb=20170529070609")
    paginas.append(embed3)

    # Mensaje inicial
    current = 0
    message = await ctx.send(embed=paginas[current])

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == message.id
            and str(reaction.emoji) in ["⬅️", "➡️"]
        )

    while True:
        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️":
                current = (current + 1) % len(paginas)
                await message.edit(embed=paginas[current])
                await message.remove_reaction(reaction, ctx.author)

            elif str(reaction.emoji) == "⬅️":
                current = (current - 1) % len(paginas)
                await message.edit(embed=paginas[current])
                await message.remove_reaction(reaction, ctx.author)

        except asyncio.TimeoutError:
            break

# ==========================
# Ayuda con botones
# ==========================

@bot.command(name="help_chao")
async def help_chao(ctx):
    """Muestra ayuda detallada de todos los comandos"""
    view = HelpView()
    await ctx.send(embed=view.pages[0], view=view)

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.pages = [
            self.page_crianza(),
            self.page_entrenamiento(),
            self.page_tiendas(),
            self.page_economia_animales(),
            self.page_misc()
        ]
        self.current_page = 0

    def page_crianza(self):
        embed = discord.Embed(
            title="🐣 Crianza y Cuidado (1/5)",
            description="Comandos básicos para criar, cuidar y disciplinar tu Chao.",
            color=discord.Color.green()
        )
        embed.add_field(name="`$adoptar`", value="Adopta un huevo con nombre y color opcional.", inline=False)
        embed.add_field(name="`$sacudir`", value="Sacude suavemente el huevo.", inline=False)
        embed.add_field(name="`$acariciar`", value="Muestra afecto y aumenta felicidad.", inline=False)
        embed.add_field(name="`$silbar`", value="Haz que tu Chao venga o que el huevo se mueva.", inline=False)
        embed.add_field(name="`$lanzar`", value="Rompe el cascarón o maltrata al Chao.", inline=False)
        embed.add_field(name="`$golpear`", value="Golpea al Chao, reduciendo su felicidad.", inline=False)
        embed.add_field(name="`$regañar`", value="Regaña al Chao si se porta mal.", inline=False)
        embed.add_field(name="`$ignorar`", value="Ignora al Chao, reduciendo apego.", inline=False)
        return embed

    def page_entrenamiento(self):
        embed = discord.Embed(
            title="💪 Información y Entrenamiento (2/5)",
            description="Mejora las habilidades, consulta estado y evoluciona.",
            color=discord.Color.blue()
        )
        embed.add_field(name="`$mi_chao`", value="Ver estadísticas y datos actuales del Chao.", inline=False)
        embed.add_field(name="`$goodbye`", value="Despídete de tu Chao para siempre.", inline=False)
        embed.add_field(name="`$entrenar_swim/fly/run/power`", value="Entrena habilidades específicas.", inline=False)
        embed.add_field(name="`$alimentar <fruta>`", value="Dale comida para reducir hambre y subir stats.", inline=False)
        embed.add_field(name="`$usar_juguete <juguete>`", value="Interactúa con juguetes y gana recompensas.", inline=False)
        embed.add_field(name="`$tocar_instrumento <instrumento>`", value="Toca canciones interactivas.", inline=False)
        embed.add_field(name="`$evolucionar`", value="Evoluciona si cumple requisitos.", inline=False)
        return embed

    def page_tiendas(self):
        embed = discord.Embed(
            title="🛒 Tiendas y Compras (3/5)",
            description="Adquiere alimentos, atuendos, juguetes y herramientas.",
            color=discord.Color.purple()
        )
        embed.add_field(name="`$shop_meal`", value="Ver frutas y alimentos.", inline=False)
        embed.add_field(name="`$shop_outfits`", value="Ver atuendos y sombreros.", inline=False)
        embed.add_field(name="`$shop_toys`", value="Ver juguetes disponibles.", inline=False)
        embed.add_field(name="`$shop_tools`", value="Ver herramientas útiles.", inline=False)
        embed.add_field(name="`$blackmarket`", value="Comprar ítems raros y misteriosos.", inline=False)
        embed.add_field(name="`$comprar <objeto> [cantidad]`", value="Comprar un artículo.", inline=False)
        return embed

    def page_economia_animales(self):
        embed = discord.Embed(
            title="💰 Economía y Animales (4/5)",
            description="Gana monedas, cuida animales y obtén recompensas.",
            color=discord.Color.gold()
        )
        embed.add_field(name="`$carrera`", value="Participa en una carrera interactiva por monedas.", inline=False)
        embed.add_field(name="`$reclamar_diario`", value="Recoge tu recompensa diaria.", inline=False)
        embed.add_field(name="`$animales`", value="Ver lista de animales disponibles.", inline=False)
        embed.add_field(name="`$comprar_animales <animal>`", value="Compra un animal para tu Chao.", inline=False)
        embed.add_field(name="`$usar_animales <animal>`", value="Aplica rasgos animales a tu Chao.", inline=False)
        return embed

    def page_misc(self):
        embed = discord.Embed(
            title="📚 Otros Comandos (5/5)",
            description="Comandos informativos y de gestión.",
            color=discord.Color.teal()
        )
        embed.add_field(name="`$guia`", value="Guía detallada de evolución y crianza.", inline=False)
        embed.add_field(name="`$estadisticas`", value="Muestra las partes animales aplicadas.", inline=False)
        embed.add_field(name="`$inventario`", value="Ver tu inventario completo.", inline=False)
        embed.add_field(name="`$saldo`", value="Consulta tu saldo actual de monedas.", inline=False)
        return embed

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.blurple)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="➡️ Siguiente", style=discord.ButtonStyle.blurple)
    async def siguiente(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

from discord import ui, ButtonStyle

@bot.command()
async def soporte(ctx):
    """Muestra opciones de invitación y soporte del bot"""
    embed = discord.Embed(
        title="🤝 Soporte y Enlaces",
        description=(
            "Aquí tienes enlaces útiles:\n\n"
            "🔹 **Invitar al bot:** Añádeme a tu servidor.\n"
            "🔹 **Servidor de soporte:** Únete para recibir ayuda."
        ),
        color=discord.Color.blue()
    )
    embed.set_image(url="https://i.pinimg.com/736x/4b/8c/48/4b8c4813d720aaccfc455b3d97aca78f.jpg")

    # Reemplaza estos enlaces con los tuyos:
    link_invitar = "https://discord.com/oauth2/authorize?client_id=1391564124818772048"
    link_soporte = "https://discord.gg/Zpx4D6YrSF"

    view = ui.View()
    view.add_item(ui.Button(label="✨ Invitar al Bot", url=link_invitar, style=ButtonStyle.link))
    view.add_item(ui.Button(label="🛠️ Servidor de Soporte", url=link_soporte, style=ButtonStyle.link))

    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print("✅ Bot listo y comandos cargados.")

bot.run(config.TOKEN)