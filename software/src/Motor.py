# Importa as bibliotecas necessárias
from Utils import mapValues
from machine import Pin, PWM
from time import sleep

# Classe dos Motores
class Motor:
    
    # Construtor recebe pino do motor, limites de PWM, frequência
    # e um parâmetro para ativar o pulso inicial
    def __init__(self, motorPin : int, minPWM = 51, maxPWM = 102,
                 freq : int = 50, pulse : bool = False):
        
        # Define o pino PWM com a frequência especificada
        self.__motor = PWM(Pin(motorPin), freq=freq, duty=0)
        
        # Armazena os valores mínimos e máximos de PWM
        self.__minPWM = minPWM
        self.__maxPWM = maxPWM
        
        # Velocidade atual do motor (em %)
        self.__atualVelocity = 0
        
        # Indica se o motor precisa de um pulso inicial para girar
        self.__doPulse = pulse
                
    # Desconstrutor: desliga o motor ao destruir o objeto
    def __del__(self):
        self.setVelocity(0)
    
    # Mapeia a velocidade percentual (0–100%) para valores de PWM
    def __mapVelocity(self, velocity : int):
        return int(mapValues(velocity, 0, 100, self.__minPWM, self.__maxPWM))
    
    # Gera um pulso de alta velocidade para iniciar motores fracos
    def __pulse(self, time_ms : int):
        if self.__doPulse:
            # Aplica PWM máximo por alguns milissegundos
            maxVel = self.__mapVelocity(100)
            self.__motor.duty(maxVel)
            sleep(time_ms / 1000.0)  # tempo em segundos
            
            # Retorna à velocidade desejada
            atualVel = self.__mapVelocity(self.__atualVelocity)
            self.__motor.duty(atualVel)
    
    # Define a velocidade do motor (0 a 100%)
    def setVelocity(self, velocity : int):
        # Garante que a velocidade não ultrapasse 100%
        if velocity > 100:
            print("Velocity Overflow! Setting velocity 100%")
            self.__motor.duty(self.__mapVelocity(100))
            self.__atualVelocity = 100
            return
        
        # Se a velocidade for 0 ou negativa, desliga o motor
        if velocity <= 0:
            print("Velocity is less or equal 0! Turning Off")
            self.turnOff()
            return

        # Se o motor estava parado, aplica o pulso inicial
        if self.__atualVelocity == 0:
            self.__pulse(10)
        
        # Converte a velocidade em duty cycle de PWM
        duty = self.__mapVelocity(velocity)
        
        # Calcula o tempo de pulso em microssegundos para depuração
        us = duty * 20000 / 1023
        print(f'us: {us}')        
        
        # Aplica o duty cycle no motor e atualiza a velocidade atual
        self.__motor.duty(duty)
        self.__atualVelocity = velocity
        
    # Desliga o motor (coloca no mínimo PWM permitido)
    def turnOff(self):
        self.__motor.duty(self.__minPWM)
        self.__atualVelocity = 0
