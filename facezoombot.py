#!/usr/bin/env python3

import telepot
import requests

from PIL import Image

class ZoomBot(telepot.Bot):
    def __init__(self, token):
        super(ZoomBot, self).__init__(token)

        self.helptext = """Send an image of a face and I'll zoom right in on the face."""

    def on_chat_message(self, msg):
        print("Got a message")
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            if msg['text'] == '/start' or msg['text'].startswith('/help'):
                bot.sendMessage(chat_id, self.helptext)
            if msg['text'] == '/about':
                bot.sendMessage(chat_id, "This bot is made by Jelle Besseling (@pingiun)\nHosted by @bothosting.")
            elif chat_type == 'private':
                bot.sendMessage(chat_id, self.helptext)
        elif content_type in ['new_chat_participant', 'left_chat_participant', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'channel_chat_created']:
            return
        elif content_type == 'photo':
            
            file_path = '/tmp/' + msg['photo'][-1]['file_id'] + '.jpg'
            print("Downloading file")
            bot.download_file(msg['photo'][-1]['file_id'], file_path)
            print("Recognizing faces")
            params = {'image': open(file_path, 'rb')}
            headers = {'X-Mashape-Key': TOKEN_MA, 'Accept': 'application/json'}
            request = requests.post('https://apicloud-facerect.p.mashape.com/process-file.json', files=params, headers=headers)

            faces = request.json()
            
            if len(faces['faces']) > 1 and chat_type == 'private':
                bot.sendMessage(chat_id, "There are too many faces in your photo, I only work when one face is visible. Please crop your foto to only show one face.")
            if len(faces['faces']) == 0 and chat_type == 'private':
                bot.sendMessage(chat_id, "Couldn't detect a face in your picture.")
            else:
                bot.sendChatAction(chat_id, 'upload_photo')
                face = faces['faces'][0]
                im = Image.open(file_path)
                if face['orientation'] == 'frontal':
                    dwidthleft = round((face['width'] - face['width'] * 0.6) / 2)
                    dwidthright = round((face['width'] - face['width'] * 0.6) / 2)
                    dheighttop = round((face['height'] - face['height'] * 0.4) / 2)
                    dheightbottom = round((face['height'] - face['height'] * 0.8) / 2)
                elif face['orientation'] == 'profile-left':
                    dwidthleft = round((face['width'] - face['width'] * 0.9) / 2)
                    dwidthright = round((face['width'] - face['width'] * 0.4) / 2)
                    dheighttop = round((face['height'] - face['height'] * 0.4) / 2)
                    dheightbottom = round((face['height'] - face['height'] * 0.7) / 2)
                elif face['orientation'] == 'profile-right':
                    dwidthleft = round((face['width'] - face['width'] * 0.4) / 2)
                    dwidthright = round((face['width'] - face['width'] * 0.9) / 2)
                    dheighttop = round((face['height'] - face['height'] * 0.4) / 2)
                    dheightbottom = round((face['height'] - face['height'] * 0.7) / 2)
                crop = im.crop((face['x'] + dwidthleft, face['y'] + dheighttop, face['x'] + face['width'] - dwidthright, face['y'] + face['height'] - dheightbottom))
                crop_path = '/tmp/' + msg['photo'][-1]['file_id'] + 'zoom.jpg'
                crop.save(crop_path, 'JPEG')
                bot.sendPhoto(chat_id, open(crop_path, 'rb'))
        else:
            if chat_type == 'private':
                bot.sendMessage(chat_id, "I don't get it. Use /help to find out how this bot works.")

def main():
    configfile = configparser.ConfigParser()
    configfile.read('config.ini')
    TOKEN_TG = configfile['bot']['TelegramToken']
    TOKEN_MA = configfile['bot']['MashapeToken']
    
    bot = ZoomBot(TOKEN_TG)
    bot.message_loop(run_forever=True)
