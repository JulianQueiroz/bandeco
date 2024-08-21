from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from telegram import Bot
import asyncio
import schedule
import time

TOKEN = '6774243823:AAHKjbfWiothfs-beKGDvrhtWNlOvHlrhag' 
GROUP_ID = '-4503429022'  

bot = Bot(token=TOKEN)

emojis_tipo_refeicao = {
    'ALMOÇO':'ALMOÇO - ',
    'Entrada': '🥗',
    'Prato Principal': '🍽️',
    'Prato Vegano': '🌱',
    'Guarnição': '🥕',
    'Acompanhamentos': '🍚',
    'Sobremesa': '🍰',
    'JANTAR':'JANTAR - '
}
async def enviar_cardapio():
    url = 'https://docs.google.com/spreadsheets/d/1YvCqBrNw5l4EFNplmpRBFrFJpjl4EALlVNDk3pwp_dQ/pubhtml'

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

            print(tipo_refeição)


            for index in range(1, 8):
                if index < len(td_elements):
                    dia_da_semana = list(refeições_por_dia.keys())[index - 1]
                    refeição = td_elements[index].get_text().strip()
                    refeição = re.sub(' +', ' ', refeição)
                    refeições_por_dia[dia_da_semana].append(f'{emoji_tipo_refeição}  {refeição}')
                    
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
        mensagem_almoco = f'\n'.join(almoco)
        mensagem_janta = f'\n'.join(janta)

        try:
            mensagem_enviada = await bot.send_message(chat_id=GROUP_ID, text=mensagem_almoco)
            mensagem_enviada = await bot.send_message(chat_id=GROUP_ID, text=mensagem_janta)
            print(f'Mensagens enviadas com sucesso!')
        except Exception as e:
            print(f'Erro ao enviar mensagem: {e}')

    else:
        print(f'Erro ao acessar a página: {response.status_code}')

def job():
    asyncio.run(enviar_cardapio())

schedule.every().day.at("14:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60) 