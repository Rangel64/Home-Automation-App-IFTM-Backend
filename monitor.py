from flask import Flask, jsonify, request
import json
import time
import datetime
import pytz
from firebase import firebase
import threading
from models.Relay import Relay
from models.Groups import Group

fb = firebase.FirebaseApplication('https://projetos8-default-rtdb.firebaseio.com/', None)

class MonitorThread(threading.Thread):
    def __init__(self, group: Group):
        threading.Thread.__init__(self)
        self.group = group
        self._stop_event = threading.Event()

    def run(self):
        brazil_tz = pytz.timezone('Brazil/East')  # Fuso horário brasileiro (UTC-3)
        while not self._stop_event.is_set():
            if(self.group.controll_time):
                current_time = datetime.datetime.now(brazil_tz).strftime("%H:%M")
                if self.group.time_on <= current_time < self.group.time_off:
                    for relay_id in self.group.relays:
                        activate_relay(relay_id)
                else:
                    for relay_id in self.group.relays:
                        deactivate_relay(relay_id)
            if(self.group.controll_pot):
                metrics = fb.get("/","pzem")
                metrics = json.loads(metrics)
                current_pot = metrics["power"]     
                if self.group.pot_min<=current_pot and current_pot<=self.group.pot_max:
                    for relay_id in self.group.relays:
                        activate_relay(relay_id)
                else:
                    for relay_id in self.group.relays:
                        deactivate_relay(relay_id)         
            time.sleep(1)  

    def stop(self):
        self._stop_event.set()

def activate_relay(relay_id: int):
    data = fb.get("/relays",str(relay_id))
    isManual = data['isManual']
    if(not isManual):
        fb.put(f"/relays/{relay_id}", "state", True)
        fb.put("/relay",str(relay_id),True)

def deactivate_relay(relay_id: int):
    data = fb.get("/relays",str(relay_id))
    isManual = data['isManual']
    if(not isManual):
        fb.put(f"/relays/{relay_id}", "state", False)
        fb.put("/relay",str(relay_id),False)

def check_for_new_and_deleted_groups(existing_groups, monitor_threads):
    while True:
        data = fb.get("/", "groups")
        current_group_ids = set(data.keys()) if data else set()

        # Detect new groups
        new_group_ids = current_group_ids - existing_groups
        for group_id in new_group_ids:
            print("id",group_id)
            print("add")
            group_data = data[group_id]
            id = group_id
            name = group_data['name']
            controll_pot = group_data['controll_pot']
            controll_time = group_data['controll_time']
            pot_max = float(group_data['pot_max'])
            pot_min = float(group_data['pot_min'])
            time_off = group_data['time_off']
            time_on = group_data['time_on']
            relays = group_data['relays'].replace('"', '').split(',')
            relays = [int(x) for x in relays]
            group = Group(id=id,name=name, controll_pot=controll_pot, controll_time=controll_time, pot_max=pot_max, pot_min=pot_min, time_off=time_off, time_on=time_on, relays=relays)
            existing_groups.add(group_id)
            # if group.controll_pot or group.controll_time:
            monitor_thread = MonitorThread(group)
            monitor_thread.daemon = True
            monitor_thread.start()
            monitor_threads[group_id] = monitor_thread

        # Detect deleted groups
        deleted_group_ids = existing_groups - current_group_ids
        print(monitor_threads)
        for group_id in deleted_group_ids:
            print("deleted")
            
            monitor_threads[group_id].stop()
            del monitor_threads[group_id]
            existing_groups.remove(group_id)

        time.sleep(1)  # Verifica novos e deletados grupos a cada minuto

