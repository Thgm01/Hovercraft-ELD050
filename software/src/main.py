#===============================================================
# Bibliotecas
#===============================================================

from machine import Pin
import network
import time
from time import sleep
import json
from umqtt.robust import MQTTClient  # Biblioteca para comunicação MQTT robusta
import sys
import math

# Módulos personalizados
from Hovercraft import Hovercraft
import Utils

# Define o modo de controle (True: com servo, False: com ventoinhas diretamente)
controlWithServo = True

# Instancia o Hovercraft com o pino do servo (caso esteja presente)
hovercraft = Hovercraft(panServoPin=27)

#===============================================================
# Wi-Fi e Node-Red
#===============================================================

# Configurações da rede Wi-Fi
WIFI_SSID     = 'raspi-webgui'
WIFI_PASSWORD = 'raspberrypi'

# Configurações MQTT
mqtt_client_id = 'esp_gp_thi_ma_ro'
MQTT_IO_URL = "172.20.10.2"  # Endereço IP do broker MQTT (por exemplo, o Raspberry Pi)

#===============================================================
# Conecta o ESP ao roteador Wi-Fi
#===============================================================

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)  # Usa a interface Wi-Fi em modo estação (cliente)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    if not wifi.isconnected():
        print('Conectando...')
        timeout = 0
        while (not wifi.isconnected() and timeout < 30):
            print(10 - timeout)
            timeout += 1
            time.sleep(1)
    if wifi.isconnected():
        print('Conectado')
    else:
        print('Nao conectado')
        sys.exit()  # Encerra o programa se não conseguir conectar

# Chama a função para conectar ao Wi-Fi
connect_wifi()

# Instancia o cliente MQTT (sem usuário/senha)
client = MQTTClient(client_id=mqtt_client_id , server=MQTT_IO_URL)

# Tenta conectar ao broker MQTT
try:
    client.connect()
except Exception as e:
    print('Nao foi possivel conectar ao servidor MQTT {}{}'.format(type(e).__name__, e))
    sys.exit()

#===============================================================
# Função de Callback MQTT: executa quando uma mensagem é recebida
#===============================================================
count = 0  # Contador para timeout de controle

def cb(topic, msg):
    global count

    # Processa comandos do joystick
    if topic == b'hovercraft/joystick':
        dict_msg = json.loads(msg.decode('utf-8'))  # Decodifica mensagem JSON
        joystick_x = dict_msg['vector']['x']
        joystick_y = dict_msg['vector']['y']
        joystickAngle = dict_msg['angle']['radian']
        module = int(dict_msg['distance'])  # Intensidade da direção
        cos = math.cos(joystickAngle)      # Projeção do ângulo no eixo X

        if not controlWithServo:
            # Modo de controle por ventoinhas (sem servo)
            velMotorLeft = module
            velMotorRight = module - module * cos
            
            if joystick_x < 0:
                velMotorLeft = module + module * cos
                velMotorRight = module
            
            if joystick_y < 0:  # Joystick para trás => parar
                velMotorLeft = 0
                velMotorRight = 0
            
            hovercraft.controlWithFan(velMotorLeft, velMotorRight)
            print(velMotorLeft)
            print(velMotorRight)

        else:
            # Modo de controle com servo para direcionamento
            velocity = module
            angle = 45 * cos  # Ângulo proporcional ao eixo X
            
            # Verifica se o joystick está parado
            if abs(module - 0) < 0.05:
                angle = 0
                velocity = 0
            if joystick_y < 0:  # Joystick para trás => parar
                angle = 0
                velocity = 0
            
            count = 0  # Reinicia o timeout

            # Mapeia o ângulo do joystick para o intervalo do servo
            angle = Utils.mapValues(angle, -90, 90, 35, -35)
            print(angle)

            # Define o ângulo e velocidade
            hovercraft.controlWithServo(angle, Utils.mapValues(module, 0, 100, 30, 100))

    # Processa o comando para ativar/desativar os motores de sustentação
    if topic == b'hovercraft/enable_lift_fans':
        print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
        hovercraft.toggleLiftMotorsState()

#===============================================================
# Inscrição nos tópicos MQTT e configuração do callback
#===============================================================

# Define a função callback
client.set_callback(cb)

# Inscreve-se nos tópicos de controle
client.subscribe(b'hovercraft/joystick')           # Controle de movimento
client.subscribe(b'hovercraft/enable_lift_fans')   # Ativar/desativar sustentação

#===============================================================
# Loop principal
#===============================================================

while True:
    try:
        # Verifica se há novas mensagens MQTT recebidas
        client.check_msg()

        # Se não receber comandos por muito tempo, para os motores
        if count < 100:
            count += 1
        else:
            hovercraft.controlWithServo(0, 0)  # Parar o hovercraft
        
    except:  # Se ocorrer erro (por exemplo, desconexão)
        client.disconnect()
        sys.exit()  # Encerra o programa
