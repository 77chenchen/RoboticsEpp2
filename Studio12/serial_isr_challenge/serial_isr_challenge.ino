

#include <avr/io.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdint.h>
#include <util/delay.h>

// ============================================================
// PACKET DEFINITIONS  
// ============================================================

#define MAX_STR_LEN   32
#define PARAMS_COUNT  16

typedef enum {
  PACKET_TYPE_COMMAND  = 0,
  PACKET_TYPE_RESPONSE = 1,
  PACKET_TYPE_MESSAGE  = 2,
} TPacketType;

typedef enum {
  COMMAND_ESTOP = 0,
} TCommandType;

typedef enum {
  RESP_OK     = 0,
  RESP_STATUS = 1,
} TResponseType;

// TPacket: 1 + 1 + 2 + 32 + (16 * 4) = 100 bytes.
typedef struct {
  uint8_t  packetType;
  uint8_t  command;
  uint8_t  dummy[2];
  char     data[MAX_STR_LEN];
  uint32_t params[PARAMS_COUNT];
} TPacket;

typedef enum {
  STATE_RUNNING = 0,
  STATE_STOPPED = 1,
} TButtonState;

// ============================================================
// CIRCULAR TX BUFFER
// ============================================================

#define TX_BUFFER_SIZE  128
#define TX_BUFFER_MASK  (TX_BUFFER_SIZE - 1)

static volatile uint8_t tx_buf[TX_BUFFER_SIZE];
static volatile uint8_t tx_head = 0;
static volatile uint8_t tx_tail = 0;

// ============================================================
// CIRCULAR RX BUFFER
// ============================================================

#define RX_BUFFER_SIZE  128
#define RX_BUFFER_MASK  (RX_BUFFER_SIZE - 1)

static volatile uint8_t rx_buf[RX_BUFFER_SIZE];
static volatile uint8_t rx_head = 0;
static volatile uint8_t rx_tail = 0;

// ============================================================
// Part A: txEnqueue
// ============================================================

bool txEnqueue(const uint8_t *data, uint8_t len) {
  uint8_t localHead, localTail;
  uint8_t used, freeSpace;

  // Read shared indices once
  localHead = tx_head;
  localTail = tx_tail;

  // One slot must always remain empty to distinguish full vs empty
  used = (localHead - localTail) & TX_BUFFER_MASK;
  freeSpace = (TX_BUFFER_SIZE - 1) - used;

  if (len > freeSpace) {
    return false;
  }

  // Copy all bytes into the TX ring buffer
  for (uint8_t i = 0; i < len; i++) {
    tx_buf[localHead] = data[i];
    localHead = (localHead + 1) & TX_BUFFER_MASK;
  }

  // Publish new head only after all bytes are copied
  tx_head = localHead;

  // Enable Data Register Empty interrupt so ISR starts sending
  UCSR0B |= (1 << UDRIE0);

  return true;
}

// ============================================================
// Part B: USART Data Register Empty ISR
// ============================================================

ISR(USART_UDRE_vect) {
  if (tx_tail != tx_head) {
    UDR0 = tx_buf[tx_tail];
    tx_tail = (tx_tail + 1) & TX_BUFFER_MASK;
  }

  // If buffer is empty after sending, disable UDRE interrupt
  if (tx_tail == tx_head) {
    UCSR0B &= ~(1 << UDRIE0);
  }
}

// ============================================================
// BARE-METAL USART INITIALISATION
// ============================================================

void usartInit(uint16_t ubrr) {
  UBRR0H = (uint8_t)(ubrr >> 8);
  UBRR0L = (uint8_t)(ubrr);
  UCSR0B = (1 << TXEN0) | (1 << RXEN0) | (1 << RXCIE0);
  UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

// ============================================================
// Part C: rxDequeue
// ============================================================

bool rxDequeue(uint8_t *data, uint8_t len) {
  uint8_t localHead, localTail;
  uint8_t available;

  localHead = rx_head;
  localTail = rx_tail;

  available = (localHead - localTail) & RX_BUFFER_MASK;

  if (len > available) {
    return false;
  }

  for (uint8_t i = 0; i < len; i++) {
    data[i] = rx_buf[localTail];
    localTail = (localTail + 1) & RX_BUFFER_MASK;
  }

  rx_tail = localTail;
  return true;
}

// ============================================================
// Part D: RX Complete ISR
// ============================================================

ISR(USART_RX_vect) {
  uint8_t byte = UDR0;  // must read immediately
  uint8_t next = (rx_head + 1) & RX_BUFFER_MASK;

  // If full, discard the byte
  if (next == rx_tail) {
    return;
  }

  rx_buf[rx_head] = byte;
  rx_head = next;
}

// ============================================================
// Part E: setup() and loop()
// ============================================================

void setup() {
  usartInit(103);   // 9600 baud @ 16 MHz
  sei();            // enable global interrupts
}

void loop() {
  // Send periodic status packet
  TPacket txPacket;
  memset(&txPacket, 0, sizeof(txPacket));
  txPacket.packetType = PACKET_TYPE_RESPONSE;
  txPacket.command = RESP_STATUS;
  txPacket.params[0] = STATE_RUNNING;

  while (!txEnqueue((const uint8_t *)&txPacket, sizeof(TPacket))) {
    // non-blocking API, but loop waits until buffer can accept whole packet
  }

  // Try to receive one full packet
  TPacket rxPacket;
  if (rxDequeue((uint8_t *)&rxPacket, sizeof(TPacket))) {
    if (rxPacket.packetType == PACKET_TYPE_COMMAND &&
        rxPacket.command == COMMAND_ESTOP) {

      TPacket okPacket;
      memset(&okPacket, 0, sizeof(okPacket));
      okPacket.packetType = PACKET_TYPE_RESPONSE;
      okPacket.command = RESP_OK;

      while (!txEnqueue((const uint8_t *)&okPacket, sizeof(TPacket))) {
        // wait until there is enough TX space
      }
    }
  }

  _delay_ms(1000);
}