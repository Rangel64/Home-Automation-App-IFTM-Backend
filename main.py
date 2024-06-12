from flask import Flask, jsonify, request
import json
import time
from firebase import firebase
import threading
from models.Relay import Relay
from models.Groups import Group
from monitor import MonitorThread,check_for_new_and_deleted_groups

fb = firebase.FirebaseApplication('https://pi8iftm-default-rtdb.firebaseio.com/', None)

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    global response
    return "<h1>PI8-Backend</h1>"  

@app.route('/reset_id_groups', methods = ['GET'])
def reset_id_groups():
    for i in range(1,9,1):
        fb.put("/relays/"+str(i),"id_group","-1")
    return {'response':""}

@app.route('/get_relays', methods = ['GET'])
def get_relays():
    global response,fb
    data = fb.get("/","relays")

    try:
    
        if(data!=None):
            data.remove(None)
            relays = []
            for value in data:
                id = value['id']
                id_group = value['id_group']
                isManual = value['isManual']
                state = value['state']
                relays.append(Relay(id=id,id_group=id_group, isManual=isManual,state=state))
        relays_response = []
        
        for relay in relays:
            if(relay.id_group == "-1"):
                relays_response.append(relay.toJson())
            
        return{"response":relays_response}
        
    except Exception as e:
        print(f"Erro ao coletar os dados do Firebase: {e}")
        return {'response':[]}

@app.route('/get_relays_group', methods = ['POST'])
def get_relays_group():
    global response,fb
    request_data = json.loads(request.data.decode('utf-8'))
    data = fb.get("/","relays")
   
    try:
        if(data!=None):
            data.remove(None)
            relays = []
            for value in data:
                id = value['id']
                id_group = value['id_group']
                isManual = value['isManual']
                state = value['state']
                relays.append(Relay(id=id,id_group=id_group, isManual=isManual,state=state))
        relays_response = []
        
        for relay in relays:
            if(relay.id_group == request_data["id"]):
                relays_response.append(relay.toJson())
            
        return{"response":relays_response}
        
    except Exception as e:
        print(f"Erro ao coletar os dados do Firebase: {e}")
        return {'response':[]}

@app.route('/get_relays_control', methods = ['GET'])
def get_relays_control():
    global response,fb
    data = fb.get("/","relays")
   
    try:
        if(data!=None):
            data.remove(None)
            relays = []
            for value in data:
                id = value['id']
                id_group = value['id_group']
                isManual = value['isManual']
                state = value['state']
                relays.append(Relay(id=id,id_group=id_group, isManual=isManual,state=state))
        relays_response = []
        
        for relay in relays:
            relays_response.append(relay.toJson())
        
        return{"response":relays_response}
        
    except Exception as e:
        print(f"Erro ao coletar os dados do Firebase: {e}")
        return {'response':[]}
        

@app.route('/set_activate_relay', methods = ['POST'])
def set_activate_relay():
    global response,fb
    request_data = json.loads(request.data.decode('utf-8'))
    
    
    try:
        response = fb.put("/relays",request_data["id"],data=request_data)
        response = fb.put("/relay",request_data["id"],request_data["state"])
        return {'response':["Done"]}
    
    except Exception as e:
        print(f"Erro ao adicionar dados ao Firebase: {e}")
        return {'response':["fail"]}

@app.route('/get_metrics', methods = ['GET'])
def get_metrics():
    global response,fb
    metrics = fb.get("/","pzem")
    metrics = json.loads(metrics)     
    return {'response':metrics}

@app.route('/get_groups', methods = ['GET'])
def get_groups():
    global response,fb
    data = fb.get("/","groups")
    
    try:
        if(data!=None):
            groups = []
            for key, value in data.items():
                id = key
                name = value['name']
                controll_pot = value['controll_pot']
                controll_time = value['controll_time']
                pot_max = float(value['pot_max'])
                pot_min = float(value['pot_min'])
                time_off = value['time_off']
                time_on = value['time_on']
                relays = value['relays'].replace('"', '').split(',')
                relays = [int(x) for x in relays]
                groups.append(Group(id=id,name=name, controll_pot=controll_pot, controll_time=controll_time, pot_max=pot_max, pot_min=pot_min, time_off=time_off, time_on=time_on, relays=relays))
            
        groups_response = []
       
        for group in groups:
            groups_response.append(group.toJson())
            
        
        return{"response":groups_response}
    except Exception as e:
        print(f"Erro ao coletar os dados do Firebase: {e}")
        return {'response':[]}
    
    

@app.route('/set_group', methods = ['POST'])
def set_group():
    global response,fb
    request_data = json.loads(request.data.decode('utf-8'))
    relays = request_data["relays"].replace("[","").replace("]","")
    request_data["relays"] = relays

    try:
        a = fb.post("/groups",data=request_data)

        relays = request_data["relays"].replace("[","").replace("]","")
        relays = relays.replace('"', '').split(',')
        relays = [int(x) for x in relays]
       
        for i in relays:
            fb.put("/relays/"+str(i),"id_group",a["name"])
            fb.put("/relays/"+str(i),"/isManual",False)
        
        data = fb.get("/","groups")
        
        if(data!=None):
            groups = []
            for key, value in data.items():
                id = key
                name = value['name']
                controll_pot = value['controll_pot']
                controll_time = value['controll_time']
                pot_max = float(value['pot_max'])
                pot_min = float(value['pot_min'])
                time_off = value['time_off']
                time_on = value['time_on']
                relays = value['relays'].replace('"', '').split(',')
                relays = [int(x) for x in relays]
                groups.append(Group(id=id,name=name, controll_pot=controll_pot, controll_time=controll_time, pot_max=pot_max, pot_min=pot_min, time_off=time_off, time_on=time_on, relays=relays))
            
            if(len(groups)<=1):
                start_monitoring()
                
        return {'response':"done"}
    
    except Exception as e:
        print(f"Erro ao adicionar dados ao Firebase: {e}")
        return {'response':"fail"}
    

@app.route('/delete_group', methods = ['POST'])
def delete_groups():
    global response,fb
    request_data = json.loads(request.data.decode('utf-8'))
    # print(request_data)
    try:
        if(request_data!=None):
            relays = request_data["relays"].replace("[","").replace("]","")
            relays = relays.replace('"', '').split(',')
            relays = [int(x) for x in relays]

            for relay_ in relays:
                fb.put("/relays/"+str(relay_),"/id_group","-1")
                fb.put("/relays/"+str(relay_),"/isManual",False)
                fb.put("/relays/"+str(relay_),"/state",False)
                
                fb.put("/relay/",str(relay_),False)
                

            fb.delete("/groups",request_data["id"])   

            return{'response':"done"}
        return{"response":""}
    except Exception as e:
        print(f"Erro ao coletar os dados do Firebase: {e}")
        return {'response':"fail"}

@app.route('/start_monitoring', methods=['GET'])
def start_monitoring():
    data = fb.get("/", "groups")
    print(data)
    if data:
        groups = []
        for key, value in data.items():
            id = key
            name = value['name']
            controll_pot = value['controll_pot']
            controll_time = value['controll_time']
            pot_max = float(value['pot_max'])
            pot_min = float(value['pot_min'])
            time_off = value['time_off']
            time_on = value['time_on']
            relays = value['relays'].replace('"', '').split(',')
            relays = [int(x) for x in relays]
            groups.append(Group(id=id,name=name, controll_pot=controll_pot, controll_time=controll_time, pot_max=pot_max, pot_min=pot_min, time_off=time_off, time_on=time_on, relays=relays))
        existing_groups = set(group.id for group in groups)
        monitor_threads = {}

        for group in groups:
            # if group.controll_pot or group.controll_time:
            monitor_thread = MonitorThread(group)
            monitor_thread.daemon = True
            monitor_thread.start()
            monitor_threads[group.id] = monitor_thread

        check_thread = threading.Thread(target=check_for_new_and_deleted_groups, args=(existing_groups, monitor_threads))
        check_thread.daemon = True
        check_thread.start()

        return jsonify(response="Monitoring started"), 200

    return jsonify(response="No groups to monitor"), 200
  
if(__name__ == "__main__"):
    app.run(host="localhost", port=5000,debug=True)

    
