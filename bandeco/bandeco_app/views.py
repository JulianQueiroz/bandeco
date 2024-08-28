from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from telegram import Bot
import asyncio
import schedule
import time
from telegram.constants import ParseMode

TOKEN = '6774243823:AAEze-l5MMGYUsVHLy9QGnKYzub5rt78rh8' 
GROUP_ID = '-1002231687187'  

bot = Bot(token=TOKEN)

emojis_tipo_refeicao = {
    'ALMOÇO':'ALMOÇO -',
    'Entrada': '🥗',
    'Prato Principal': '🍽️',
    'Prato Vegano': '🌱',
    'Guarnição': '🥕',
    'Acompanhamentos': '🍚',
    'Sobremesa': '🍰',
    'JANTAR':'JANTAR -',
    'Fechado': 'Fechado'
}
def escape_markdown_v2(text):
    """
    Escape caracteres especiais do Markdown V2 no Telegram.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def enviar_cardapio():
    urls = [
        ('https://docs.google.com/spreadsheets/d/1gymUpZ2m-AbDgH7Ee7uftbqWmKBVYxoToj28E8c-Dzc/pubhtml',"PV/IFCS"),
        ('https://docs.google.com/spreadsheets/d/1YvCqBrNw5l4EFNplmpRBFrFJpjl4EALlVNDk3pwp_dQ/pubhtml',"Fundão")
        ]
    for url, local in urls:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            tr_elements = soup.find_all('tr')[2:-1]

            refeições_por_dia = {
                'Segunda-feira': [],
                'Terça-feira': [],
                'Quarta-feira': [],
                'Quinta-feira': [],
                'Sexta-feira': [],
                'Sábado': [],
                'Domingo': []
            }

            for tr in tr_elements:
                td_elements = tr.find_all('td')

                tipo_refeição = td_elements[0].get_text().replace('(temos opção sem molho)', '').strip()
                emoji_tipo_refeição = emojis_tipo_refeicao.get(tipo_refeição, '')



                for index in range(1, 8):
                    if index < len(td_elements):
                        dia_da_semana = list(refeições_por_dia.keys())[index - 1]
                        refeição = td_elements[index].get_text().strip()
                        refeição = re.sub(' +', ' ', refeição)
                        refeições_por_dia[dia_da_semana].append('\n' + f'{emoji_tipo_refeição}  {refeição}')
                        
            hoje = datetime.now().strftime("%A")
            dia_da_semana = {
                'Monday': 'Segunda-feira',
                'Tuesday': 'Terça-feira',
                'Wednesday': 'Quarta-feira',
                'Thursday': 'Quinta-feira',
                'Friday': 'Sexta-feira',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }.get(hoje, 'Segunda-feira')

            cardapio_do_dia = refeições_por_dia.get(dia_da_semana, [])
            almoco = cardapio_do_dia[0:7]
            janta = cardapio_do_dia[8:-1]
            mensagem_almoco =  '\n'.join(almoco) + f'\n\n\n📍 - *{local}* \n'
            mensagem_janta =  '\n'.join(janta) + f'\n\n\n📍 - *{local}* \n'
            print(mensagem_almoco)
            print(mensagem_janta)
            try:
                mensagem_enviada = await bot.send_message(chat_id=GROUP_ID, text=mensagem_almoco, parse_mode=ParseMode.MARKDOWN)
                mensagem_enviada = await bot.send_message(chat_id=GROUP_ID, text=mensagem_janta, parse_mode=ParseMode.MARKDOWN)
                print(f'Mensagens enviadas com sucesso!')
            except Exception as e:
                print(f'Erro ao enviar mensagem: {e}')

        else:
            print(f'Erro ao acessar a página: {response.status_code}')

asyncio.run(enviar_cardapio())
