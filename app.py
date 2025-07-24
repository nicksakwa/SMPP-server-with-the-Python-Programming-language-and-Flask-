import os
from flask import Flask, render_template, request, flask, redirect, url_for
from smpplib import client
from smpplib import const
from dotenv import  load_dotenv

load_dotenv()

app= Flask(__name__)
app.secret_key= os.urandom(24)

HOST= os.getenv('SMPP_HOST', 'smpp2.infobip.com')
PORT = int(os.getenv('SMPP_PORT', 8887))
SYSTEM_ID= os.getenv('INFOBIP_SYSTEM_ID')
PASSWORD= os.getenv('INFOBIP_PASSWORD')

def  send_smpp_message(sender_id, recipient_number,message_text):
    if not all([SYSTEM_ID, PASSWORD]):
        return False, "SMPP credentials (SYSTEM_ID, PASSWORD) are not configured."
    
    cl=None
    try:
        cl=client.Client(HOST,PORT)
        cl.connect(True)
        pdu=cl.bind_transciever(system_id=SYSTEM_ID.encode('ascii'), password=PASSWORD.encode('ascii'))
        
        if pdu.command_status==const.SMPP_ESMK_ROK:
            app.logger.info("Successfully bound to Infobip SMPP.")

            message_pdu=cl.send_message(
                
            )
