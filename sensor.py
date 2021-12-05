from __future__ import annotations
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, ATTR_ATTRIBUTION, CONF_ID
    )
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA,SensorEntity)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle
import requests
import json
#from bs4 import BeautifulSoup


_LOGGER=logging.getLogger(__name__)

TIME_BETWEEN_UPDATES = timedelta(minutes=60)

DEFAULT_NAME = 'qzwater'
CONF_CUSTNO = 'custno'
CONF_TOKEN = 'token'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CUSTNO): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_NAME, default= DEFAULT_NAME): cv.string
    }
)

HEADERS = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicehall.wegist.cn/',
    'Origin': 'https://servicehall.wegist.cn',
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate'
}
API_URL = "https://apiservicehall.wegist.cn/index.php/wap/Customeraccount/query_account_arrearage"

def setup_platform(hass: HomeAssistant,config: ConfigType,add_entities: AddEntitiesCallback,discovery_info: DiscoveryInfoType | None = None) -> None:
    _LOGGER.info("Setup platform sensor.qzwater")
    custno = config.get(CONF_CUSTNO)
    sensor_name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)
    query_dict = {"company_id": 366,"customer_code": custno}
    #water=QZWater(sensor_name,query_dict)
    add_entities([QZWater(token,sensor_name,query_dict)])

class QZWater(SensorEntity):
    def __init__(self,token,sensor_name,query_dict):
        self.attributes = {}
        self._state = None
        self._query_dict = query_dict
        self._name = sensor_name
        self._token = token

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return 'mdi:cup-water'

    @property
    def device_state_attributes(self):
        return self.attributes

    @property
    def unit_of_measurement(self):
        return "元"

    @Throttle(TIME_BETWEEN_UPDATES)
    def update(self):
        # try:
        response = requests.post(API_URL + "?caid=612&token=" + self._token,params=self._query_dict,headers = HEADERS)
        # except ReadTimeout:
        #     _LOGGER.error("Connection timeout....")
        # except ConnectionError:
        #     _LOGGER.error("Connection Error....")
        # except RequestException:
        #     _LOGGER.error("Unknown Error")

        jsondata = response.text #将python对象转为JSON字符串
        data=json.loads(jsondata)
        waterFee = data["data"]["PrepayAmt"]
        code = data["data"]["Code"]
        name = data["data"]["Name"]
        #_LOGGER.info("waterFee=" + waterFee)
        self._state = waterFee #余额
        self.attributes['Code'] = code #户号
        self.attributes['Name'] = name #户主
