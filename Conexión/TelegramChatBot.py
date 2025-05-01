import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------------- CONFIGURACIÓN DE GOOGLE SHEETS ---------------- #
# Alcances (scopes) para acceder a Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

# Autenticación con el archivo JSON
creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo
sheet = client.open("Cuentas & Telegram").sheet1  # Cambia el nombre si tu hoja se llama diferente

# Función para guardar mensajes
def guardar_mensaje(usuario, mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([fecha_hora, usuario, mensaje])

# ---------------- CONFIGURACIÓN DEL BOT DE TELEGRAM ---------------- #
TELEGRAM_TOKEN = '8153041663:AAFtgq2Q5Zsr2LCsA8wx8wP9uKE334meU-w'

# Función que maneja los mensajes recibidos
#async def mensaje_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #usuario = update.message.from_user.full_name
    #texto = update.message.text

    #guardar_mensaje(usuario, texto)

    # Opcional: Confirmación al usuario
    #await update.message.reply_text("✅ Mensaje guardado en Google Sheets.")
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
