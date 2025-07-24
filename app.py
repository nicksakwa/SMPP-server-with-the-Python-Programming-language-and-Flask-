import os
from flask import Flask, render_template, request, flash, redirect, url_for
from smpplib import client
from smpplib import const
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24) # A secret key for flashing messages

# Infobip SMPP connection details from environment variables
HOST = os.getenv('SMPP_HOST', 'smpp2.infobip.com')
PORT = int(os.getenv('SMPP_PORT', 8887))
SYSTEM_ID = os.getenv('INFOBIP_SYSTEM_ID')
PASSWORD = os.getenv('INFOBIP_PASSWORD')

def send_smpp_message(sender_id, recipient_number, message_text):
    """
    Function to send an SMS message via SMPP using smpplib.
    Returns True on success, False on failure, along with a message.
    """
    if not all([SYSTEM_ID, PASSWORD]):
        return False, "SMPP credentials (SYSTEM_ID, PASSWORD) are not configured."

    cl = None
    try:
        cl = client.Client(HOST, PORT)
        cl.connect(True)  # True for SSL/TLS

        pdu = cl.bind_transceiver(system_id=SYSTEM_ID.encode('ascii'), password=PASSWORD.encode('ascii'))

        if pdu.command_status == const.SMPP_ESME_ROK:
            app.logger.info("Successfully bound to Infobip SMPP.")

            message_pdu = cl.send_message(
                source_addr_ton=const.SMPP_TON_ALPHANUMERIC,
                source_addr_npi=const.SMPP_NPI_UNKNOWN,
                source_addr=sender_id.encode('ascii'),
                dest_addr_ton=const.SMPP_TON_INTERNATIONAL,
                dest_addr_npi=const.SMPP_NPI_E164,
                destination_addr=recipient_number.encode('ascii'),
                short_message=message_text.encode('latin1'), # Use latin1 for basic chars, utf-8 for wider range
                registered_delivery=1, # Request delivery report
                data_coding=3 # Latin-1 encoding (or 8 for UCS-2/Unicode)
            )

            if message_pdu.command_status == const.SMPP_ESME_ROK:
                app.logger.info(f"Submit SM successful. Message ID: {message_pdu.message_id}")
                return True, f"Message sent successfully! Message ID: {message_pdu.message_id}"
            else:
                app.logger.error(f"Failed to submit SM. Status: {message_pdu.command_status}")
                return False, f"Failed to send message. SMPP Status: {message_pdu.command_status}"
        else:
            app.logger.error(f"Failed to bind to Infobip SMPP. Status: {pdu.command_status}")
            return False, f"Failed to connect to SMPP gateway. Bind Status: {pdu.command_status}"

    except Exception as e:
        app.logger.exception("An error occurred during SMPP communication.")
        return False, f"An error occurred: {e}"
    finally:
        if cl:
            try:
                cl.unbind()
                cl.disconnect()
            except Exception as e:
                app.logger.warning(f"Error during SMPP unbind/disconnect: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sender_id = request.form['sender_id']
        recipient_number = request.form['recipient_number']
        message_text = request.form['message_text']

        success, message = send_smpp_message(sender_id, recipient_number, message_text)

        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('index')) # Redirect to clear form on refresh

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False in production