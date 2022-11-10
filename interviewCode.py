### comunication
### tabela padrão de comunicação
# Coluna 1: Endereço do registrador em decimal
# Coluna 2: Endereço do registrador em hexadecimal 
# Coluna 3: Número de bytes para formar o dado completo
# Coluna 4: Descrição dos dados nos registradores em questão 
# Coluna 5: Forma de conversão
# Coluna 6: Após tratamento, qual o tipo de dado para conversão

###requisicao em hex
# Byte1 - Unidade do equipamento
# Byte2 - Tipo de função a ser realizada (03 = leitura, 06 = gravação)
# Byte3 - Primeira parte do endereço do registrador
# Byte4 - Segunda parte do endereço do registrador
# Byte5 - Primeira parte do número de registradores a serem lidos em sequência
# Byte6 - Segunda parte do número de registradores a serem lidos em sequência
# Byte7 e Byte8 = número de confirmação calculado a partir de uma tabela CRC (não importante para agora)


# Teste 1:
# A partir da solicitação: solicitação = “0503c5700006f95b” Utilizando a tabela 2, o que foi solicitado?
###########
# solicitado ao equipamento numero 05, funcao 03 (leitura), com endereco hexadecimal C570,
# com numero de registrador a serem lidos 0006 e numero de confirmacao f95b!
###########
# Obtivemos a resposta: “05030c000000e000000176000000e55726'”
# Utilizando a linguagem Python3, é solicitado ao candidato tratar e traduzir a resposta do equipamento.

class deviceResponse():
    def __init__(self, msg:str):
        self.HexMSG = msg
    def extractMSG(self):
        self.device = int(self.HexMSG[:2], 16) 
        self.function = int(self.HexMSG[2:4], 16)
        self.bytesResponse = int(self.HexMSG[4:6], 16) ## value will change depending on klaus response
        self.response = [] ## join by registers
        for i in range(6,6+self.bytesResponse*2,4): # i start from the 6th and go until the end of the double of the number of bytes response, the step is 4 cause this is the amount of bits in a register
            self.response.append(int(self.HexMSG[i:i+4], 16)) 
        self.confirmation = int(self.HexMSG[i:], 16)

        
resposta = deviceResponse("05030c000000e000000176000000e55726")
resposta.extractMSG()
print(resposta.response)


# Teste 2:
# A) Com a ferramenta MQTT X (sugestão) e com auxílio da biblioteca “paho.mqtt”, configurar conexão cliente [4] enviar o “payload” (JSON) disponibilizado.
# {
# "loadshifting" : 0,
# "peakshaving" : 0,
# "charging" : 0
# }
# loadshifting bool
# "peakshaving" [kW]
# "charging" bool

import paho.mqtt.client as mqtt
import json
import random


P1 = { "loadshifting" : 0, "peakshaving" : 10, "charging" : 0}
P2 = { "loadshifting" : 0, "peakshaving" : 20, "charging" : 0}
P3 = { "loadshifting" : 0, "peakshaving" : 30, "charging" : 0}
peakshavingThreshold = 20


broker = 'broker.emqx.io'
port = 1883
topic = "python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client(client_id)
    #client.username_pw_set(username, p^assword)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg):
    # Serializing json  
    if type(msg) is dict: ## convert my dict to json
        json_data = json.dumps(msg) 
    elif type(msg) is str:
        json_data = msg
    else:
        print("msg not valid")
        return
        
    result = client.publish(topic, json_data)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{json_data}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


client = connect_mqtt()
client.loop_start()
publish(client, P1)
client.loop_stop()


# B) Enviar mensagem MQTT via código (a ser visualizado na ferramenta MQTT X ou semelhante)
# indicando se: algumas das P1, P2 ou P3 estão abaixo do “threshold” definido pelo peakshaving

def thresholdValidation(client, payloadname: str, payload: dict, threshold: int):
    if payload["peakshaving"] < threshold:
        client.loop_start()
        publish(client, payloadname +  " peakshaving below the threshold defined!")
        client.loop_stop()

thresholdValidation(client, "P1", P1, peakshavingThreshold)
thresholdValidation(client, "P2", P2, peakshavingThreshold)
thresholdValidation(client, "P3", P3, peakshavingThreshold)


