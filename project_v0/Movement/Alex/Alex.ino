
// =============================================================
// Arduino setup() and loop()
// =============================================================

void setup() {
}

void loop() {
    forward(130); // takes values from 0 to 255
    delay(2000);

    ccw(130); // takes values from 0 to 255
    delay(2000);

    backward(130); // takes values from 0 to 255
    delay(2000);

    cw(130); // takes values from 0 to 255
    delay(2000);

    stop();
    delay(4000);
}
