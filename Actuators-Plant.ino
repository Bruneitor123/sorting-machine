// ---- H-bridge control pins ----
// First actuator (first pusher)
const int A1_IN1 = 8;   // extend
const int A1_IN2 = 9;   // retract

// Second actuator (second pusher)
const int A2_IN1 = 10;  // extend
const int A2_IN2 = 11;  // retract

const int PUSH_TIME_MS = 350;

void setup() {
  Serial.begin(9600);

  pinMode(A1_IN1, OUTPUT);
  pinMode(A1_IN2, OUTPUT);
  pinMode(A2_IN1, OUTPUT);
  pinMode(A2_IN2, OUTPUT);

  stopAll();
}

void stopAll() {
  digitalWrite(A1_IN1, LOW);
  digitalWrite(A1_IN2, LOW);
  digitalWrite(A2_IN1, LOW);
  digitalWrite(A2_IN2, LOW);
}

// ---- helpers ----

void firstExtendFor(int ms) {
  digitalWrite(A1_IN1, HIGH);
  digitalWrite(A1_IN2, LOW);
  delay(ms);
  stopAll();
}

void firstRetractFor(int ms) {
  digitalWrite(A1_IN1, LOW);
  digitalWrite(A1_IN2, HIGH);
  delay(ms);
  stopAll();
}

void secondExtendFor(int ms) {
  digitalWrite(A2_IN1, HIGH);
  digitalWrite(A2_IN2, LOW);
  delay(ms);
  stopAll();
}

void secondRetractFor(int ms) {
  digitalWrite(A2_IN1, LOW);
  digitalWrite(A2_IN2, HIGH);
  delay(ms);
  stopAll();
}

// ---- main loop: react to Python letters ----

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();   // 'R','Y','S','T','U','N'

    switch (c) {
      case 'R':   // example mapping: RED + SAND -> first actuator
      case 'S':
        firstExtendFor(PUSH_TIME_MS);
        firstRetractFor(PUSH_TIME_MS);
        break;

      case 'Y':   // YELLOW + STEEL -> second actuator
      case 'T':
        secondExtendFor(PUSH_TIME_MS);
        secondRetractFor(PUSH_TIME_MS);
        break;

      case 'U':   // unknown/aluminum -> no push
      case 'N':
      default:
        break;
    }
  }
}