from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# ---------------- CONFIGURACIÓN DE GOOGLE SHEETS ---------------- #
# Alcances (scopes) para acceder a Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde variable de entorno
google_credentials_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_credentials_json, scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo
sheet = client.open("Cuentas & Tel").sheet1  # Cambia el nombre si tu hoja se llama diferente

# Función para guardar mensajes
def guardar_mensaje(usuario, mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([fecha_hora, usuario, mensaje])

# ---------------- CONFIGURACIÓN DEL BOT DE TELEGRAM ---------------- #
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Función que maneja los mensajes recibidos
async def mensaje_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    partes = text.split(' ', 1)

    if len(partes) != 2:
        await update.message.reply_text("Formato incorrecto. Escribe:\n<valor> <concepto>\nEjemplo: 500 Compra de libros")
        return

    valor = partes[0]
    concepto = partes[1]
    
    fecha_hora_completa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    solo_fecha = datetime.now().strftime("%Y-%m-%d")

    usuario = update.message.from_user.username or update.message.from_user.full_name
    mensaje = text

    # Agregar fila a la hoja
    fila = [fecha_hora_completa, usuario, mensaje, valor, solo_fecha, concepto]
    sheet.append_row(fila)

    await update.message.reply_text("Transacción registrada ✅")

# ---------------- INICIO DEL BOT ---------------- #
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handler que escucha cualquier mensaje de texto
    handler_mensajes = MessageHandler(filters.TEXT & (~filters.COMMAND), mensaje_recibido)

    app.add_handler(handler_mensajes)

    print("🤖 Bot en funcionamiento... Esperando mensajes.")
    app.run_polling()
