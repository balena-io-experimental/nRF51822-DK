#ifndef RESIN_STATUS_SERVICE_H_
#define RESIN_STATUS_SERVICE_H_

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "ble.h"
#include "ble_srv_common.h"
#include "bsp.h"
#include "app_timer.h"
#include "app_error.h"
#include "SEGGER_RTT.h"

#define BLE_UUID_RESIN_STATUS_BASE_UUID       {{0x23, 0xD1, 0x13, 0xEF, 0x5F, 0x78, 0x23, 0x15, 0xDE, 0xEF, 0x12, 0x12, 0x00, 0x00, 0x00, 0x00}}
#define BLE_UUID_RESIN_STATUS_SERVICE         0xF00D
#define BLE_UUID_RESIN_FLASH_CHARACTERISTIC   0xBEEF
#define BLE_UUID_RESIN_RESTART_CHARACTERISTIC 0xFEED
#define BLE_UUID_RESIN_APP_CHARACTERISTIC     0xFEEE

APP_TIMER_DEF(m_flash_timer_id);
#define FLASH_TIMER_INTERVAL                  APP_TIMER_TICKS(250, 0)
int timerTotal;

typedef struct
{
    uint16_t                    conn_handle;
    uint16_t                    service_handle;
    ble_gatts_char_handles_t    char_handles;
} ble_os_t;

void resin_status_service_init(ble_os_t * p_resin_status_service);
void resin_status_service_on_ble_evt(ble_os_t * p_resin_status_service, ble_evt_t * p_ble_evt);

#endif
