# Importa as classes Motor e Servo, além da função sleep
from Motor import Motor
from Servo import Servo
from time import sleep

# Classe que representa um Hovercraft com motores de sustentação e propulsão
class Hovercraft:
    
    # Construtor da classe
    def __init__(self,
                 liftFanPins: list = [32],         # Pinos dos ventiladores de sustentação
                 leftMotorPin: int = 33,           # Pino do motor esquerdo
                 rightMotorPin: int = 16,          # Pino do motor direito
                 panServoPin: int = None):         # Pino do servo (opcional)
        
        # Cria a lista de motores de sustentação
        self.__liftMotors = list()
        for pin in liftFanPins:
            self.__liftMotors.append(Motor(pin))
        
        # Envia os sinal para iniciar o motor BLDC
        for liftMotor in self.__liftMotors:
            liftMotor.setVelocity(0)
            sleep(3)  
        
        # Flag que indica se os motores de sustentação estão ativos
        self.__liftMotorsEnable = False
        
        # Cria os motores esquerdo e direito com limite de PWM reduzido
        self.__leftMotor = Motor(leftMotorPin, maxPWM=72)
        self.__rightMotor = Motor(rightMotorPin, maxPWM=72)

        # Inicializa o servo de pan (opcional)
        print(panServoPin)
        self.__panServo = None
        if panServoPin != None:
            self.__panServo = Servo(panServoPin)
            print(self.__panServo)
    
    # Ativa os motores de sustentação com 35% da velocidade
    def enableLiftMotors(self):
        for liftMotor in self.__liftMotors:
            liftMotor.setVelocity(35)
        self.__liftMotorsEnable = True
    
    # Desativa os motores de sustentação
    def disableLiftMotors(self):
        for liftMotor in self.__liftMotors:
            liftMotor.setVelocity(0)
        self.__liftMotorsEnable = False
    
    # Alterna o estado dos motores de sustentação (liga/desliga)
    def toggleLiftMotorsState(self):
        if self.__liftMotorsEnable:
            self.disableLiftMotors()
        else:
            self.enableLiftMotors()
        
        return self.__liftMotorsEnable  # Retorna o novo estado
    
    # Retorna o status dos motores de sustentação (True = ligados, False = desligados)
    def getLiftMotorsStatus(self):
        return self.__liftMotorsEnable
    
    # Controla o hovercraft usando o servo para direcionamento e motores para propulsão
    def controlWithServo(self, angle : int, velocity : int):
        if self.__panServo == None:
            print('Hovercraft without pan Servo')
            return
        elif not self.__liftMotorsEnable:
            print('Hovercraft\'s Lift Motors disable')
            return
        
        # Define o ângulo do servo
        self.__panServo.setAngle(angle)
        
        # Define a mesma velocidade para os dois motores de propulsão
        self.__leftMotor.setVelocity(velocity)
        self.__rightMotor.setVelocity(velocity)
    
    # Controla o hovercraft diretamente pelos dois motores de propulsão (sem servo)
    def controlWithFan(self, velocityMotorLeft : int, velocityMotorRight : int):
        if not self.__liftMotorsEnable:
            print('Hovercraft\'s Lift Motors disable')
            return
        
        # Centraliza o servo, se estiver presente
        if self.__panServo != None:
            self.__panServo.setAngle(0)
        
        # Define velocidades independentes para os motores esquerdo e direito
        self.__leftMotor.setVelocity(velocityMotorLeft)
        self.__rightMotor.setVelocity(velocityMotorRight)
