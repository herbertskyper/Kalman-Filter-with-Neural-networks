#include <Servo.h>

constexpr int maxAngle = 150;
constexpr int minAngle = 30;
constexpr int pwmTop = 3;
constexpr int pwmBottom = 5;
constexpr int baudRate = 9600;


Servo servoBottom;
Servo servoTop;
 
void setup()
{
  Serial.begin(baudRate);
  servoTop.attach(pwmTop, 500, 2500);
  servoBottom.attach(pwmBottom, 500, 2500);
}

void regulate(int &angle)
{
  if(angle<0) angle=0;
  else if(angle>180) angle=180;
}
 
void loop()
{
  while(Serial.available()>=6)
  {

    int angle1 = 0;
    for(int i=2;i>=0;i--)
    {
      int digit = Serial.read();
      angle1 += (digit-'0')*pow(10, i);
    }
    Serial.print("Top:");
    Serial.print(angle1);

    int angle2 = 0;
    for(int i=2;i>=0;i--)
    {
      int digit = Serial.read();
      angle2 += (digit-'0')*pow(10, i);
    }
    Serial.print("Bottom:");
    Serial.println(angle2);

    regulate(angle1);
    regulate(angle2);

    servoTop.write(angle1);
    servoBottom.write(angle2);
    delay(30);
  }
}