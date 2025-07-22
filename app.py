from smpplib import client
from smpplib import const

HOST='smpp2.infobip.com'
PORT= 8887
SYSTEM_ID='your_infobip_smpp_username'
PASSWORD='your_info_smpp_password'
SENDER_ID='YourCompany'
RECIPIENT_NUMBER="2567xxxxxxxxx"
MESSAGE_TEXT='Hello from Infobip via SMPP!'

cl=client.Client(HOST, PORT)
cl.connect(True)

pdu=cl.bind_transceiver(system_id=SYSTEM_ID, password=PASSWORD)
print(f"Bind response: {pdu.command_status}")

if pdu.command_status == const.SMPP_ESME_ROK:
    print("Successfully bound to Infobip SMPP.")

    message_pdu= cl.send_message(
        source_addr_ton=const.SMPP_TON_ALPHANUMERIC,
        source_addr_npi=const.SMPP_NPI_UNKNOWN,
        source_addr=SENDER_ID.encode('ascii'),
        dest_addr_ton=const.SMPP_TON_INTERNATIONAL,
        dest_addr_npi=const.SMPP_NPI_E164,
        destination_addr=RECIPIENT_NUMBER.encode('ascii'),
        short_message=MESSAGE_TEXT.encode('latin1'),
        registered_delivery=1,
        data_coding=3
    )
    print(f"Submit SM response:"){message_pdu.command_status}, Message ID:{mesage_pdu.message_id}")
    cl.unbind()
    cl.disconnect()
else:
    print(f"Failed to bind:{pdu.command_status}")
