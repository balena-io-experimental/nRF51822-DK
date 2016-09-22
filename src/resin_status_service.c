#include "resin_status_service.h"

#define RTT_PRINTF(...) \
do { \
    char str[64];\
    sprintf(str, __VA_ARGS__);\
    SEGGER_RTT_WriteString(0, str);\
 } while(0)


static uint32_t add_flash_characteristic(ble_os_t * p_resin_status_service)
{
    uint32_t            err_code;
    ble_uuid_t          char_uuid;
    ble_uuid128_t       base_uuid = BLE_UUID_RESIN_STATUS_BASE_UUID;
    char_uuid.uuid    = BLE_UUID_RESIN_FLASH_CHARACTERISTIC;
    err_code = sd_ble_uuid_vs_add(&base_uuid, &char_uuid.type);
    APP_ERROR_CHECK(err_code);

    ble_gatts_char_md_t char_md;
    memset(&char_md, 0, sizeof(char_md));
    char_md.char_props.read = 0;
    char_md.char_props.write = 1;

    ble_gatts_attr_md_t attr_md;
    memset(&attr_md, 0, sizeof(attr_md));
    attr_md.vloc      = BLE_GATTS_VLOC_STACK;

    //BLE_GAP_CONN_SEC_MODE_SET_OPEN(&attr_md.read_perm);
    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&attr_md.write_perm);

    ble_gatts_attr_t            attr_char_value;
    memset(&attr_char_value, 0, sizeof(attr_char_value));
    attr_char_value.p_uuid    = &char_uuid;
    attr_char_value.p_attr_md = &attr_md;

    attr_char_value.max_len     = 1;
    attr_char_value.init_len    = 1;
    uint8_t value[1]            = {0x00};
    attr_char_value.p_value     = value;

    err_code = sd_ble_gatts_characteristic_add(p_resin_status_service->service_handle,
                                      &char_md,
                                      &attr_char_value,
                                      &p_resin_status_service->char_handles);
    APP_ERROR_CHECK(err_code);

    return NRF_SUCCESS;
}

static uint32_t add_restart_characteristic(ble_os_t * p_resin_status_service)
{
    uint32_t            err_code;
    ble_uuid_t          char_uuid;
    ble_uuid128_t       base_uuid = BLE_UUID_RESIN_STATUS_BASE_UUID;
    char_uuid.uuid    = BLE_UUID_RESIN_RESTART_CHARACTERISTIC;
    err_code = sd_ble_uuid_vs_add(&base_uuid, &char_uuid.type);
    APP_ERROR_CHECK(err_code);

    ble_gatts_char_md_t char_md;
    memset(&char_md, 0, sizeof(char_md));
    char_md.char_props.read = 0;
    char_md.char_props.write = 1;

    ble_gatts_attr_md_t attr_md;
    memset(&attr_md, 0, sizeof(attr_md));
    attr_md.vloc      = BLE_GATTS_VLOC_STACK;

    //BLE_GAP_CONN_SEC_MODE_SET_OPEN(&attr_md.read_perm);
    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&attr_md.write_perm);

    ble_gatts_attr_t            attr_char_value;
    memset(&attr_char_value, 0, sizeof(attr_char_value));
    attr_char_value.p_uuid    = &char_uuid;
    attr_char_value.p_attr_md = &attr_md;

    attr_char_value.max_len     = 1;
    attr_char_value.init_len    = 1;
    uint8_t value[1]            = {0x00};
    attr_char_value.p_value     = value;

    err_code = sd_ble_gatts_characteristic_add(p_resin_status_service->service_handle,
                                      &char_md,
                                      &attr_char_value,
                                      &p_resin_status_service->char_handles);
    APP_ERROR_CHECK(err_code);

    return NRF_SUCCESS;
}

static void on_ble_write(ble_os_t * p_resin_status_service, ble_evt_t * p_ble_evt)
{
    if(p_ble_evt->evt.gatts_evt.params.write.handle == 22)
    {
        timerTotal = 0;
        uint32_t err_code;

        err_code = app_timer_stop(m_flash_timer_id);
        APP_ERROR_CHECK(err_code);

        err_code = app_timer_start(m_flash_timer_id, FLASH_TIMER_INTERVAL, NULL);
        APP_ERROR_CHECK(err_code);
    }
    else if(p_ble_evt->evt.gatts_evt.params.write.handle == 24)
    {
        NVIC_SystemReset();
    }
}

static void timer_timeout_handler(void * p_context)
{
    uint32_t err_code;
    if(timerTotal % 2 == 0)
    {
        err_code = bsp_indication_set(BSP_INDICATE_USER_STATE_ON);
        APP_ERROR_CHECK(err_code);
    }
    else
    {
        err_code = bsp_indication_set(BSP_INDICATE_USER_STATE_OFF);
        APP_ERROR_CHECK(err_code);
    }

    timerTotal++;

    if(timerTotal >= 40)
    {
        err_code = app_timer_stop(m_flash_timer_id);
        APP_ERROR_CHECK(err_code);

        err_code = bsp_indication_set(BSP_INDICATE_ADVERTISING);
        APP_ERROR_CHECK(err_code);
    }
}

void resin_status_service_init(ble_os_t * p_resin_status_service)
{
    uint32_t            err_code;
    ble_uuid_t          service_uuid;
    ble_uuid128_t       base_uuid = BLE_UUID_RESIN_STATUS_BASE_UUID;
    service_uuid.uuid = BLE_UUID_RESIN_STATUS_SERVICE;
    err_code = sd_ble_uuid_vs_add(&base_uuid, &service_uuid.type);
    APP_ERROR_CHECK(err_code);

    p_resin_status_service->conn_handle = BLE_CONN_HANDLE_INVALID;

    err_code = sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY,
                                    &service_uuid,
                                    &p_resin_status_service->service_handle);
    APP_ERROR_CHECK(err_code);

    err_code = app_timer_create(&m_flash_timer_id, APP_TIMER_MODE_REPEATED, timer_timeout_handler);
    APP_ERROR_CHECK(err_code);

    add_flash_characteristic(p_resin_status_service);
    add_restart_characteristic(p_resin_status_service);
}

void resin_status_service_on_ble_evt(ble_os_t * p_resin_status_service, ble_evt_t * p_ble_evt)
{

    switch (p_ble_evt->header.evt_id)
    {
        case BLE_GATTS_EVT_WRITE:
            on_ble_write(p_resin_status_service, p_ble_evt);
            break;
        case BLE_GAP_EVT_CONNECTED:
            p_resin_status_service->conn_handle = p_ble_evt->evt.gap_evt.conn_handle;
            break;
        case BLE_GAP_EVT_DISCONNECTED:
            p_resin_status_service->conn_handle = BLE_CONN_HANDLE_INVALID;
            break;
        default:
            // No implementation needed.
            break;
    }
}
