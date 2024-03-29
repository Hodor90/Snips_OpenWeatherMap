#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
from weather import Weather
from hermes_python.ffi.utils import MqttOptions

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    hermes.publish_end_session(intentMessage.session_id, weather.forecast(intentMessage))


if __name__ == "__main__":
    conf = read_configuration_file(CONFIG_INI)
    weather = Weather(conf)

    mqtt_addr = "{}:{}".format(conf['global']['mqtt_ip_addr'], conf['global']['mqtt_port'])

    mqtt_opts = MqttOptions(username=conf['secret']['mqtt_user'], password=conf['secret']['mqtt_pw'], broker_address=mqtt_addr)
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("domi:searchWeatherForecast", subscribe_intent_callback).start()
