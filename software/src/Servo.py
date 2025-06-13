# Inporta as bibliotecas
from machine import Pin, PWM
from Utils import mapValues

# Classe dos Servo Motores
class Servo:
    
    # Construtor recebe o pino o angulo máximo, minimo e
    # o angulo central
    def __init__(self, servoPin : int, angleMin = 90,
                 angleMax = 110, centerAngle = 100):
        try:
            # Inicia o pino do Servo
            self.__servo = PWM(Pin(servoPin), freq=400, duty = 0)
            
            # Recebe os atributo
            self.__angleMin = angleMin
            self.__angleMax = angleMax
            self.__centerAngle = centerAngle
            
        # Caso aconteça algum erro define como None o Servo
        except ValueErro as e:
            print(f"Erro: {e}")
            self.__servo = None
            raise
    
    # Função para mapear o angulo para sinal PWM
    def __mapAngle(self, angle : int):
        return int(mapValues(angle, 0, 180, 0, 1023))
    
    # Função para aplicar os angulos
    def setAngle(self, angleDelta : int):
        
        # definindo o SP com relação ao centro
        setAngle = self.__centerAngle + angleDelta
        
        # Tratar exceções
        if setAngle > 180:
            print('Angle Overflow! Insert a valid angle')
            return
        
        if setAngle < 0:
            print('Angle Underflow! Insert a valid angle')
            return
        
        # Passa para o Servo motor o sinal em PWM
        self.__servo.duty(self.__mapAngle(setAngle))
        
        
        
    
        
            