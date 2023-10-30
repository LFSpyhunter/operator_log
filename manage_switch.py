#!/usr/bin/python3
import re
import pexpect
import sys
import ast
import os
from func import check_ip, change_date
from jinja2 import Environment, FileSystemLoader
from operator_api import switch_port_args, abort
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user
from func_for_switch import define_model, define_state_ports, define_vlans, get_id_abon
import requests


SWITCH = {}


class Switch:
    def __init__(self):
        self.connection = ""      
        self.ip = ""
        self.model = ""

    def view(self, ip):
        self.ip = ip
        self.model = define_model(ip)
        ports_info_dict = {"state": {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: "", 13: "", 14: "", 15: "", 16: "", 17: "", 18: "", 19: "", 20: "", 21: "", 22: "", 23: "", 24: "", 25: "", 26: "", 27: "", 28: ""},
                           "link": {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: "", 13: "", 14: "", 15: "", 16: "", 17: "", 18: "", 19: "", 20: "", 21: "", 22: "", 23: "", 24: "", 25: "", 26: "", 27: "", 28: ""},
                           "speed": {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: "", 13: "", 14: "", 15: "", 16: "", 17: "", 18: "", 19: "", 20: "", 21: "", 22: "", 23: "", 24: "", 25: "", 26: "", 27: "", 28: ""},
                           "errors": {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: "", 13: "", 14: "", 15: "", 16: "", 17: "", 18: "", 19: "", 20: "", 21: "", 22: "", 23: "", 24: "", 25: "", 26: "", 27: "", 28: ""},
                           "desc": {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: "", 13: "", 14: "", 15: "", 16: "", 17: "", 18: "", 19: "", 20: "", 21: "", 22: "", 23: "", 24: ""},
                           "vlans": {1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: "", 13: "", 14: "", 15: "", 16: "", 17: "", 18: "", 19: "", 20: "", 21: "", 22: "", 23: "", 24: "", 25: "", 26: "", 27: "", 28: ""}}

        vlan_list_ports = define_vlans(self.ip)
        for i in range(1, 29):
            state, link, speed, error, desc = define_state_ports(
                self.ip, i)
            ports_info_dict['state'][i] = self.state_port(state)
            if link == '1':
                ports_info_dict['link'][i] = "UP"
            else:
                ports_info_dict['link'][i] = "Down"
            ports_info_dict['speed'][i] = speed + " Мбит/c"
            ports_info_dict['errors'][i] = error
            ports_info_dict['desc'][i] = desc
            ports_info_dict['vlans'][i] = ", ".join(vlan_list_ports[i])
        return render_template('switch.html', ports=ports_info_dict, model=self.model, ip=self.ip, connection=self.connection)

    def state_port(self, port):
        if port == '1':
            state = "enable"
        else:
            state = "disable"
        return state

    def port_info(self):
        args = switch_port_args.parse_args()
        result = {}
        port = args['port']
        request_result_acl = requests.get(f'http://192.168.255.70:9999/sw/{self.ip}/ports/{port}/acl')
        if request_result_acl.json()['data']:
            if request_result_acl.json()['data'][0]['ip']:
                result['Профиль 10'] = request_result_acl.json()['data'][0]['ip']
                # result['Договор'] = get_id_abon(result['Профиль 10'])
            if request_result_acl.json()['data'][1]['ip']:
                result['Профиль 20'] = request_result_acl.json()['data'][1]['ip']
            
        request_result_full = requests.get(f'http://192.168.255.70:9999/sw/{self.ip}/ports/{port}')
        try:
            result['Длинна кабеля'] = ['Пара: {} статус: {} длина: {}'.format(i['pair'],i['state'],i['len'] ) for i in request_result_full.json()['data'][0]['cable']]
        except:
            result['Длинна кабеля'] = "не показывает"
        
        request_result_mac = requests.get(f'http://192.168.255.70:9999/sw/{self.ip}/ports/{port}/mac')
        if request_result_mac.json()['data']:
            result['MAC адрес'] = request_result_mac.json()['data'][0]['mac']
        print(result)
        return result

    def set_port(self):
        if current_user.permission['admin_user'] == "enable" or current_user.permission['set_port'] == "enable":
            port = request.form.get("port")
            state = request.form.get("set_port")
            vlan_id = request.form.get("id_vlan")
            vlan_action = request.form.get("set_vlan")
            descrip = request.form.get("descrip")
            acl = request.form.get("acl")
            acl_action = request.form.get("set_acl")
            if state:
                state_port = f'conf ports {port} state {state}'
                self.set_cmd_through_telnet(state_port)
            if vlan_id:
                if vlan_action == 'add':
                    vlan_port = f'conf vlan {vlan_id} {vlan_action} unt {port}'
                else:
                    vlan_port = f'conf vlan {vlan_id} {vlan_action} {port}'
                self.set_cmd_through_telnet(vlan_port)
            if descrip:
                desc_port = f'conf ports {port} desc {descrip}'
                self.set_cmd_through_telnet(desc_port)
            if acl:
                if acl_action == 'add':
                    acl_port = [f'config access_profile profile_id 10 {acl_action} access_id {port} ip source_ip {acl} port {port} permit',
                                f'config access_profile profile_id 20 {acl_action} access_id {port} ip source_ip 0.0.0.0 port {port} deny']
                else:
                    acl_port = [f'config access_profile profile_id 10 {acl_action} access_id {port}',
                                f'config access_profile profile_id 20 {acl_action} access_id {port}']
                for cmd in acl_port:
                    self.set_cmd_through_telnet(cmd)
            return self.view(self.ip)
        else:
            return abort(401)

    def set_cmd_through_telnet(self, cmd):
        if self.connection:
            result = self.send_command(cmd)
        else:
            self.connection = self.telnet()
            result = self.send_command(cmd)
        return result

    def send_command(self, cmd):
        expect_list = {f'{self.model[0]}:(5|admin)#(?![^ ])': 'break',
                       'Refresh': 'q', 'All': 'a', 'more': ' '}
        out = ""
        try:
            self.connection.sendline(cmd)
            while True:
                match = self.connection.expect(list(expect_list.keys()))
                out += self.connection.before

                send_key = list(expect_list.values())[match]
                if send_key == "break":
                    break
                else:
                    self.connection.sendline(send_key)
            return out

        except:
            return out

    def telnet(self):
        connection = pexpect.spawn(
            f'telnet {self.ip}', encoding='utf-8', timeout=5)
        connection.expect('[Uu]ser[Nn]ame:')
        connection.sendline('link')
        connection.expect('[Pp]ass[Ww]ord:')
        connection.sendline('by:trnjh')
        connection.expect(f'{self.model[0]}:(5|admin)#(?![^ ])')
        return connection

    def logs(self):
        request_result_logs = requests.get(f'http://192.168.255.70:9999/sw/{self.ip}/log')
        logs = request_result_logs.json()['data']
        for i in logs:
            i["timestamp"] = change_date(i["timestamp"])
        return render_template('switchlog.html', logs=logs)

    def save(self):
        cmd = "save"
        self.set_cmd_through_telnet(cmd)
        flash("Успешно")
        return self.view(self.ip)

    def get_info_from_acl_per(self, value):
        try:
            match = re.search(
                r'config access_profile profile_id 10 \D+ access_id (\d+) \D+ source_ip (\S+).* port (\d+)', value)
            out = match.groups()
        except:
            return "отсутствует"
        return out[1]

    def get_info_from_acl_deny(self, value):
        try:
            match = re.search(
                r'config access_profile profile_id 20 \D+ access_id (\d+) \D+ source_ip (\S+).* port (\d+)', value)
            out = match.groups()
        except:
            return "отсутствует"
        return out[1]

    def get_info_from_diag(self, value: str):
        return value[255:]

    def get_info_from_mac(self, value):
        try:
            match = re.search(
                r'([a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2})', value)
            out = match.groups()
        except:
            return "отсутствует"
        return out

    def set_switch_info(self):
        get_config = ""
        return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=get_config)

    # def download(self):
    #     self.config = {}
    #     _, _, net, _ = self.ip.split('.')
    #     self.config = {'ip': '', 'net' : '', 'vlans' : [], 'conf_vlans' : [], 'acl' : [], 'ports' : [], 'bandwith' : []}
    #     self.config['ip'] = self.ip
    #     self.config['net'] = net
    #     self.regex_list = {'system_location': "config snmp system_location ([^>]+)",
    #                        'vlans': "create vlan (\S+)",
    #                        'igmp_member': "1500 \D+ member\S+ (\S+)",
    #                        'acl': "config access_profile profile_id 10 \D+ access_id (\d+) \D+ source_ip (\S+).* port (\d+)",
    #                        'conf_vlans': "config vlan (\S+ add \S+ \S+)",
    #                        'bandwith': "config bandwidth_control (\S+) rx_rate (\S+) tx_rate (\S+)"}
    #     for i in range(1, 25):
    #         port = define_state_ports(self.ip, i)
    #         self.config['ports'].append([i, self.state_port(port[0]), port[4]])
    #     result = self.connect_switch(self.ip)
    #     result = result.replace('\r', '').split('\n')
    #     for line in result:
    #         self.get_regex_value(line)
    #     return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config)

    def get_regex_value(self, line):       
        line = line.replace('\n', "")
        for key, value in self.regex_list.items():
            match = re.search(r'{}'.format(value), line)
            if match:
                if key == 'system_location':
                    self.config[key] = match.groups()[0]
                elif key == 'vlans':
                    self.config[key].append(match.groups()[0])
                elif key == 'conf_vlans':
                    self.config[key].append(match.groups()[0])
                elif key == 'acl':
                    self.config[key].append(
                        [match.groups()[0], match.groups()[1], match.groups()[2]])
                elif key == 'igmp_member':
                    self.config[key] = match.groups()[0]
                elif key == 'ports':
                    self.config[key].append([match.groups()[0],match.groups()[1]])
                elif key == 'ip':
                    self.config[key] = match.groups()[0]
                elif key == 'bandwith':
                    if match.groups()[1] == "no_limit" and match.groups()[2] == "no_limit":
                        pass
                    else:
                        self.config[key].append(
                            [match.groups()[0], match.groups()[1], match.groups()[2]])

    def download_from_file(self, ip):
        self.ip = check_ip(ip)
        if not self.ip:
            flash("Некорректный IP")
            return redirect("/setswitch", 302)
        self.regex_list = {'system_location': "config snmp system_location ([^>]+)",
                           'vlans': "create vlan (\S+)",
                           'igmp_member': "1500 \D+ member\S+ (\S+)",
                           'ports': "config ports (\S+).* state (\S+)",
                           'acl': "config access_profile profile_id 10 \D+ access_id (\d+) \D+ source_ip (\S+).* port (\d+)",
                           'conf_vlans': "config vlan (\S+ add \S+ \S+)",
                           'ip': "config ipif .* ipaddress (\S+)/"}
        self.config = {'ip': '', 'net' : '', 'vlans' : [], 'conf_vlans' : [], 'acl' : [], 'ports' : []}
        with open('/home/Braa/sw-backup/{}.cfg'.format(self.ip), 'r') as h:
            for line in h:
                self.get_regex_value(line)
        _, _, net, _ = self.config['ip'].split('.')
        self.config['net'] = net
        return render_template('setswitch.html', ip=self.ip, get_config=self.config)

    def get_config(self, ip, timeout=3):
        """Функция для получения конфига коммутатора"""
        config = pexpect.spawn(
            f'telnet {ip}', encoding='utf-8', timeout=timeout)
        config.expect('[Uu]ser[Nn]ame:')
        config.sendline('link')
        config.expect('[Pp]ass[Ww]ord:')
        config.sendline('by:trnjh')
        config.expect('#')
        config.sendline('show conf cur')
        config.sendline('a')
        config.expect(pexpect.TIMEOUT)
        config.sendline('logout')
        config.close()
        return config.before

    def create_dir(self, ip):
        """Функция создания папки"""
        try:
            os.makedirs(f"{sys.path[0]}/config/{ip}/")
        except FileExistsError:
            # directory already exists
            pass

    def connect_switch(self, ip):
        """Функция подключения к коммутатору взависимости от модели"""
        model = self.model[0]
        if model == 'DES-3028G':
            result = self.get_config(ip, timeout=3)
        elif model == 'DGS-1210-28X/ME':
            result = self.get_config(ip, timeout=45)
        elif model == 'DGS-3000-26TC':
            result = self.get_config(ip, timeout=30)
        elif model == 'DES-3200-28':
            result = self.get_config(ip, timeout=10)
        elif model == 'DES-3200-28/C1':
            result = self.get_config(ip, timeout=30)
        elif model == 'DES-3526':
            result = self.get_config(ip, timeout=10)
        else:
            print("Неизвестная модель")
        return result

    def upload(self):
        model = request.form.get("model")
        self.default_enable = request.form.get("def_en")
        self.config = ast.literal_eval(request.form.get("dl_config"))
        if model == 'DGS-1210-28X/ME':
            model = '1210'
            self.sw_tmp = self.create_template_config(model)
            return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config, template=self.sw_tmp)
        elif model == 'DES-3200-28/C1':
            model = '3200_c1'
            self.sw_tmp = self.create_template_config(model)
            return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config, template=self.sw_tmp)
        elif model == 'DES-3200-28':
            model = '3200'
            self.sw_tmp = self.create_template_config(model)
            return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config, template=self.sw_tmp)
        elif model == 'DES-3028G':
            model = '3028g'
            self.sw_tmp = self.create_template_config(model)
            return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config, template=self.sw_tmp)
        elif model == 'DGS-3000-26TC':
            model = '3000'
            self.sw_tmp = self.create_template_config(model)
            return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config, template=self.sw_tmp)
        elif model == 'DES-3526':
            model = '3526'
            self.sw_tmp = self.create_template_config(model)
            return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config, template=self.sw_tmp)
        else:
            print("нет такой модели")

    def upload_config(self):
        """Функция загрузки конфига из шаблона"""
        ip = request.form.get("ip_download")
        # self.sw_tmp= ast.literal_eval(request.form.get("upl_config"))
        self.sw_tmp = self.sw_tmp.split('\n')
        config = pexpect.spawn(f'telnet {ip}', encoding='utf-8', timeout=3)
        config.expect('[Uu]ser[Nn]ame:')
        config.sendline('link')
        config.expect('[Pp]ass[Ww]ord:')
        config.sendline('by:trnjh')
        config.expect('#')
        for i in self.sw_tmp:
            print(i)
            config.sendline(i)
            config.expect('#')
        config.sendline('logo')
        config.close()
        flash("Успех")
        return render_template('setswitch.html', model=self.model, ip=self.ip, get_config=self.config)

    def create_template_config(self, model):
        """Функция загрузки шаблона"""
        env = Environment(loader=FileSystemLoader(
            f'{sys.path[0]}/default_config'))
        if self.default_enable == "on":
            temp = env.get_template(f"default_config_{model}.txt")
        else:
            temp = env.get_template(f"config_{model}.txt")
        result = temp.render(self.config)
        return result


def switch_view():
    ip = ""
    ports_info_dict = ""
    model = ""
    if request.method == "POST":
        global SWITCH
        SWITCH[f'{current_user.name}'] = Switch()
        ip = request.form.get("ip_switch")
        ip = check_ip(ip)
        if not ip:
            flash("Некорректный IP")
            return redirect("/switch", 302)
        return SWITCH[f'{current_user.name}'].view(ip)
    else:
        return render_template('switch.html', ports=ports_info_dict, model=model, ip=ip)


def port_info():
    if SWITCH[f'{current_user.name}'] != "":
        return SWITCH[f'{current_user.name}'].port_info()
    else:
        flash("Соединение с коммутатором утеряно")
        return redirect("/switch")


def get_config():
    ip = request.form.get("ip_switch")
    # file = request.form.get("file")
    global SWITCH
    SWITCH[f'{current_user.name}'] = Switch()
    if ip:
        return SWITCH[f'{current_user.name}'].download_from_file(ip)
    # elif file:
    #     return SWITCH[f'{current_user.name}'].download_from_file()
    else:
        flash("Что-то пошло не так")
        return redirect("/setswitch")


def tmp_config():
    if SWITCH[f'{current_user.name}'] != "":
        return SWITCH[f'{current_user.name}'].upload()
    else:
        flash("Соединение с коммутатором утеряно")
        return redirect("/setswitch")


def set_port():
    if SWITCH[f'{current_user.name}'] != "":
        return SWITCH[f'{current_user.name}'].set_port()
    else:
        flash("Соединение с коммутатором утеряно")
        return redirect("/switch")


def set_switch():
    ip = ""
    model = ""
    if request.method == "POST":
        global SWITCH
        SWITCH[f'{current_user.name}'] = Switch()
        return SWITCH[f'{current_user.name}'].set_switch_info()
    else:
        return render_template('setswitch.html', model=model, ip=ip)


def upload_config():
    if SWITCH[f'{current_user.name}'] != "":
        return SWITCH[f'{current_user.name}'].upload_config()
    else:
        flash("Соединение с коммутатором утеряно")
        return redirect("/setswitch")


def switch_refresh():
    ip = SWITCH[f'{current_user.name}'].ip
    return SWITCH[f'{current_user.name}'].view(ip)


def switch_log():
    return SWITCH[f'{current_user.name}'].logs()


def save_switch():
    return SWITCH[f'{current_user.name}'].save()
