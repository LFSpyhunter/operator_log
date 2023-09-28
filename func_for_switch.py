#!/usr/bin/python3
import re
import requests
from easysnmp import Session
from bs4 import BeautifulSoup


def define_model(ip):
    """Функция для получения модели коммутатора"""
    session = Session(hostname=ip, community='public', version=2)
    model = session.get('SNMPv2-MIB::sysDescr.0').value
    location = session.get('SNMPv2-MIB::sysLocation.0').value
    firmware = session.get('SNMPv2-SMI::mib-2.16.19.2.0').value
    firmware_rev = session.get('SNMPv2-SMI::mib-2.16.19.3.0').value
    match = re.search(r'D\w\w-\S+', model)
    if match.group() == 'DES-3200-28/C1':
        model = "DES-3200-28"
    elif match.group() == 'DGS-1210-28X/ME/B1':
        model = "DGS-1210-28X/ME"
    else:
        model = match.group()
    firmware = f'{firmware} rev. {firmware_rev}'
    return model, location, firmware



def define_vlans(ip):
    """Функция для получения Вланов коммутатора"""
    session = Session(hostname=ip, community='public', version=2)
    vlans = session.walk('SNMPv2-SMI::mib-2.17.7.1.4.3.1.1')
    vlan_list = []
    vlan_list_ports = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [], 14: [
    ], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [], 21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: []}
    for vlan in vlans:
        vlan_list.append(vlan.value)
        vlan = vlan.value
        if vlan == "default":
            member_ports = session.get(f'.1.3.6.1.2.1.17.7.1.4.3.1.2.1')
        else:
            member_ports = session.get(f'.1.3.6.1.2.1.17.7.1.4.3.1.2.{vlan}')
        member_port = member_ports.value
        member_ports_list = []
        for c in member_port[:4]:
            result = "{0:08b}".format(ord(c))
            member_ports_list.append(result)
        member_ports_list = "".join(member_ports_list)
        member_vlan_ports = []
        for num, i in enumerate(member_ports_list, 1):
            if i == "1":
                vlan_list_ports[num].append(vlan)
                member_vlan_ports.append(str(num))
    return vlan_list_ports


def define_state_ports(ip, port):
    """Функция для получения статуса портов коммутатора"""
    session = Session(hostname=ip, community='public', version=2)
    port_state = session.get(f'IF-MIB::ifAdminStatus.{port}').value
    port_link = session.get(f'IF-MIB::ifOperStatus.{port}').value
    port_speed = session.get(f'IF-MIB::ifHighSpeed.{port}').value
    port_errors = session.get(f'IF-MIB::ifInErrors.{port}').value
    port_desc = session.get(f'IF-MIB::ifAlias.{port}').value
    return port_state, port_link, port_speed, port_errors, port_desc


def get_id_abon(ip):
    try:
        req = requests.post('http://192.168.255.251/poisk_test.php',
                            data={'ip': '{}'.format(ip), 'go99': '1'})
        soup = BeautifulSoup(req.text, 'html.parser')
        value = soup.find('input', {'name': 'id_aabon'}).get('value')       
    except AttributeError:
        value = "не найден"
    return value
