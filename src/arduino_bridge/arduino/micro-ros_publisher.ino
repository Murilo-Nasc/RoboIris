#define LEFT_DIR 8
#define LEFT_BRAKE 6
#define LEFT_PWM 9
#define RIGHT_DIR 11
#define RIGHT_BRAKE 7
#define RIGHT_PWM 10

unsigned long lastCmdTime = 0;
const unsigned long timeout = 200; // 200ms sem comando = parar

void setup() {
  Serial.begin(115200);
  
  pinMode(LEFT_DIR, OUTPUT);
  pinMode(LEFT_BRAKE, OUTPUT);
  pinMode(LEFT_PWM, OUTPUT);
  pinMode(RIGHT_DIR, OUTPUT);
  pinMode(RIGHT_BRAKE, OUTPUT);
  pinMode(RIGHT_PWM, OUTPUT);
  
  // Inicia com motores parados
  stopMotors();
}

void loop() {
  if(Serial.available()) {
    String command = Serial.readStringUntil('\n');
    int commaIndex = command.indexOf(',');
    
    if(commaIndex != -1) {
      float linear = command.substring(0, commaIndex).toFloat();
      float angular = command.substring(commaIndex + 1).toFloat();
      angular = angular / 2;
      moveMotors(linear, angular);
      lastCmdTime = millis();
    }
  }
  
  // Timeout: para os motores se não receber comandos recentes
  if(millis() - lastCmdTime > timeout) {
    stopMotors();
  }
}

void moveMotors(float linear, float angular) {
  float left = linear + angular;
  float right = linear - angular;
  
  // Motor Esquerdo
  digitalWrite(LEFT_DIR, left > 0 ? HIGH : LOW);
  analogWrite(LEFT_PWM, abs(left) * 30);
  
  // Motor Direito
  digitalWrite(RIGHT_DIR, right > 0 ? HIGH : LOW);
  analogWrite(RIGHT_PWM, abs(right) * 30);
}

void stopMotors() { 
  analogWrite(LEFT_PWM, 0);
  analogWrite(RIGHT_PWM, 0);
  digitalWrite(LEFT_BRAKE, HIGH); // Ativa freio
  digitalWrite(RIGHT_BRAKE, HIGH);
  delay(10);
  digitalWrite(LEFT_BRAKE, LOW); // Desativa freio após parar
  digitalWrite(RIGHT_BRAKE, LOW);
}
