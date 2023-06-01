import datetime
from django.http import HttpResponse
from django.shortcuts import render,redirect
import requests
from django.contrib import messages 
from rest_framework import viewsets
import urllib.parse
from datetime import date
from .models import Client,Notification,Notes,Ticket
import json

BASE_URL = 'https://prxlag01node01.zergaw.com:5101'

# Create your views here.
def home(request):
    if 'username' in request.session:
        return render(request,'home.html')
    else:
        return redirect(login)
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        username = username+"@pve"
        
        url = f"{BASE_URL}/api2/json/access/ticket"
        headers = {"content-Type": "application/x-www-form-urlencoded"}
        response1 = requests.post(url, headers=headers, data=f"username={username}&password={password}", verify=False)

        if response1.status_code == 200:
            try:
                response_json = response1.json()
            except:
                return redirect("logout")
                
            username= response_json['data']['username']
            ticket = response_json['data']['ticket']
            csrf = response_json['data']['CSRFPreventionToken']

            url2 = f"{BASE_URL}/api2/json/nodes"
            headers2 = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
            response2 = requests.get(url2,headers=headers2,verify=False)
            try:
                response_json = response2.json()
            except:
                return redirect('logout')
            nodes = response_json['data']
            request.session['username'] = username
            request.session['ticket'] = ticket
            request.session['csrf'] = csrf
            request.session['nodes'] = nodes

            response = redirect('cloudservers')
            return response
        else:
            messages.error(request,'Invalid Credentials')
            return redirect('login')
    else:
        if 'username' in request.session:
            return redirect('cloudservers')
        else:
            return render(request,'login.html')


def logout(request):
    sessions = request.session
    sessions.delete()
    response = redirect(login)
    response.delete_cookie('PVEAuthCookie')
    return response


def cloudservers(request):
    if 'username' in request.session:
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        nodes = request.session['nodes']
        try:
            vmst=[]
            for i in nodes:
                node = i['node']
                url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/"
                headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}

                response = requests.get(url,headers=headers, verify=False)
                try:
                    response_json = response.json()
                except:
                    return redirect('logout')
                if response_json['data'] != None:
                    try:
                        if response_json['data'][0]:
                            for data in response_json['data']:
                                data["node"] = node
                                vmst.append(data)
                    except:
                        pass
        except:
            messages.error(request,'Invalid Credentials')
            return redirect('login')
        try:
            response_json = response.json()
        except:
            return redirect('logout')
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')

        vmss = []
        for vms in vmst:
            vms['uptime'] = str(datetime.timedelta(seconds=vms['uptime']))
            vmss.append(vms)
        
        
        request.session['vms'] = vmss
        array = ['1','2','3','4','5']
        name = request.session['username']
        client = Client.objects.get(api_name=name)
        notifications = Notification.objects.filter(receivers = client)
        context={
            'ticket':ticket,
            'client':client,
            'array':array,
            'notifications':notifications
        }
        
        response = render(request,'dashboard.html',context)
        return response
    else:
        return redirect('login')

def console(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        vms = request.session['vms']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        for v in vms:
            if v['name'] == name:
                vm = v
        vmid = vm['vmid']
        vmname = vm['name']
        node = vm['node']

        url = 'https://prxlag01node01.zergaw.com:5101/?console=kvm&novnc=1&vmid=' + str(vmid)+ '&vmname='+ str(vmname)+'&node='+ node + '&resize=off&cmd='
        ticket = request.session['ticket']
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        context={
                'vmid':vmid,
                'vmname':vmname,
                'node':node,
                'ticket':ticket,
                'client':client,
                'url':url,
                'notifications':notifications,
            }
        response = render(request,'console.html',context)
        ticket = urllib.parse.quote(ticket, safe='')
        response.set_cookie('PVEAuthCookie',ticket,domain=BASE_URL,samesite=None,secure=True)
        return response
    else:
        return redirect('login')

def summary(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        vms = request.session['vms']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        for vm in vms:
            if vm['name'] == name:
                vms = vm
        
        request.session['vmid'] = vms['vmid']
        request.session['vmname'] = vms['name']
        request.session['node'] = vms['node']
        node = request.session['node']
        vmid = request.session['vmid']
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/status/current"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, verify=False)

        url2 = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces"
        response2 = requests.get(url2,headers=headers, verify=False)

        url3 = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/config"
        response3 = requests.get(url3,headers=headers, verify=False)

        api_name = request.session['username']
        try:
            response_json = response.json()
            response_json2 = response2.json()
            response_json3 = response3.json()
        except:
            return redirect('logout')
        vm = response_json['data']
        IPs = response_json2['data']
        notes = response_json3['data']
        api_name = request.session['username']
        
        try:
            client = Client.objects.get(api_name=api_name)
            notes = Notes.objects.get(vmid=vmid,note_by=client)
            notes = notes.notes
        except:
            notes = 'You can add your Notes here'
        
        InPs = []
        try:
            for i in IPs['result']:
                input = {'name':[],'hardwareaddress':[],'ipaddress':[]}
                name = i['name']
                hardwareaddress = i['hardware-address']
                input['name'].append(name)
                input['hardwareaddress'].append(hardwareaddress)
                for j in i['ip-addresses']:
                    ipaddress = j['ip-address']
                    input['ipaddress'].append(ipaddress)
                InPs.append(input)
        except:
            InPs = []
        vm['uptime'] = str(datetime.timedelta(seconds=vm['uptime']))
        memper = (vm['mem']*100)/vm['maxmem']
        memper = round(memper,2)
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        context={
                'ticket':ticket,
                'vm':vm,
                'memper':memper,
                'IPs':InPs,
                'notes':notes,
                'client':client,
                'notifications':notifications
            }
        response = render(request,'summary.html',context)
        return response
    else:
        return redirect('login')

def editnotes(request):
    if request.method == 'POST':
        notes = request.POST['notes']
        vmid = request.session['vmid']
        vmname = request.session['vmname']
        api_name = request.session['username']
        clientn = Client.objects.get(api_name=api_name)
        vmid = str(vmid)
        vmname = request.session['vmname']
        try:
            findnote = Notes.objects.get(vmid=vmid,note_by=clientn)
            findnote.notes = notes
            findnote.save()
            return redirect('summary',name=vmname)
        except:
            Note = Notes.objects.create(vmid=vmid,notes=notes)
            customer = Client.objects.get(api_name=api_name)
            Note.note_by.add(customer)
            Note.save()
            vmname = request.session['vmname']
            return redirect('summary',name=vmname)
    else:
        vmname = request.session['vmname']
        return redirect('summary',name=vmname)


def snapshots(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        vms = request.session['vms']
        csrf = request.session['csrf']
        for v in vms:
            if v['name'] == name:
                vm = v
        vmid = vm['vmid']
        node = vm['node']
        request.session['vmid'] = vm['vmid']
        request.session['vmname'] = vm['name']
        request.session['node']  = node
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/snapshot"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, verify=False)
        try:
            response_json = response.json()
            snapshots = response_json['data']
        except:
            return redirect('logout')
            
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        for snap in snapshots:
            try:
                snap['snaptime'] = str(date.fromtimestamp(snap['snaptime']))
            except:
                pass
        request.session['snapshots'] = snapshots
        context={
                'vm':vm,
                'client':client,
                'notifications':notifications
            }
        response = render(request,'snapshots.html',context)
        return response
    else:
        return redirect('login')

def takesnapshot(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        try:
            ram = request.POST['ram']
            ram = '1'
        except:
            ram = '0'
        csrf = request.session['csrf']
        node = request.session['node']
        ticket = request.session['ticket']
        vmid = request.session['vmid']
        params = {'snapname':name,'description':description,'vmstate':ram,'node':node,'vmid':vmid}
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/snapshot"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params, verify=False)
        
        
        vmname = request.session['vmname']
        messages.warning(request,'This may take few seconds.Your snapshots will be updated upon sucessful snapshots.')
        return redirect('snapshots',name=vmname)
    else:
        return redirect('cloudservers')

def removesnap(request):
    if request.method == 'POST':
        snapname = request.POST['snapname']
        node = request.session['node']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        vmid = request.session['vmid']
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/snapshot/{snapname}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.delete(url,headers=headers, verify=False)
        
        
        vmname = request.session['vmname']
        messages.success(request,'Removing a snapshot.')
        return redirect('snapshots',name=vmname)
    else:
        return redirect('cloudservers')

def rollbacksnap(request):
    if request.method == 'POST':
        snapname = request.POST['snapname']
        node = request.session['node']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        vmid = request.session['vmid']
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/rollback"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers, verify=False)
        vmname = request.session['vmname']
        return redirect('snapshots',vmname)
    else:
        return redirect('cloudservers')

def backup(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        vms = request.session['vms']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        for vm in vms:
            if vm['name'] == name:
                vms = vm
        storage = 'EXT_HDD_BACKUP_CLIENT'
        
        node = vms['node']
        vmid = vms['vmid']
        vmname = vms['name']
        vm=vms
        request.session['node'] = node
        request.session['vmid'] = vmid
        request.session['vmname'] = vmname
        params = {'vmid': vmid,'content':'backup'}
        url = f"{BASE_URL}/api2/json/nodes/{node}/storage/{storage}/content/"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, params=params,verify=False)
        
        try:
            response_json = response.json()
        except:
            return redirect('logout')

        bks = response_json['data']
        if bks is not None:
            number_ofbks = len(bks)
        else:
            number_ofbks = 0
        request.session['backups'] = bks
        backups = request.session['backups']
        bks = []
        try:
            for backup in backups:
                bksi = (backup['size'])/1000000000
                backup['ctime'] = str(date.fromtimestamp(backup['ctime']))
                backup['volid_edited'] = vm['name']+ '-' +str(backup['ctime'])
                backup['size'] = round(bksi,2)
            request.session['backups'] = backups
        except:
            request.session['backups'] = backups
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        context={
                'ticket':ticket,
                'vm':vm,
                'client':client,
                'notifications':notifications,
                'number_ofbks': number_ofbks
            }
        response = render(request,'backup.html',context)
        return response
    else:
        return redirect('login')

def backupnow(request):
    if 'username' in request.session:
        ticket = request.session['ticket']
        csrf = request.session['csrf']
        vms = request.session['vms']
        node = request.session['node']
        storage = 'EXT_HDD_BACKUP_CLIENT'

        notes = request.POST.get('notes')
        if notes== '':
            notes = request.session['node']
        vmid = request.session['vmid']

        params = {'vmid': vmid,'notes-template':notes,'storage':storage,'compress':'zstd','mode':'snapshot'}
        url = f"{BASE_URL}/api2/json/nodes/{node}/vzdump/"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params, verify=False)
        response_json = response.json()
        
        name =  request.session['vmname']
        messages.warning(request,'This may take few seconds.Your backups will be updated upon sucessful backup.')
        response = redirect('backup',name)
        return response
    else:
        return redirect('login')

def removebackup(request):
    if request.method == 'POST':
        volid = request.POST['volid']
        node = request.session['node']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        vmid = request.session['vmid']
        storage = 'EXT_HDD_BACKUP_CLIENT'

        urll = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/status"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(urll,headers=headers,verify=False)

        url = f"{BASE_URL}/api2/json/nodes/{node}/storage/{storage}/content/{volid}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.delete(url,headers=headers,verify=False)
        
        
        name =  request.session['vmname']
        response = redirect('backup',name)
        return response
    else:
        return redirect('cloudservers')

def restorebackup(request):
    if request.method == 'POST':
        volid = request.POST['volid']
        node = request.session['node']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        vmid = request.session['vmid']
        urll = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/status/stop"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(urll,headers=headers,verify=False)
        try:
            response_json = response.json()
        except:
            return redirect('logout')
        
        params={'vmid':vmid,'archive':volid,'force':1}
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params, verify=False)
        
        name =  request.session['vmname']
        messages.warning(request,'Restoring the backup...')
        response = redirect('backup',name)
        return response
    else:
        return redirect('cloudservers')

def vmstatus(request):
    if request.method == 'POST':
        command = request.POST['command']
        node = request.session['node']
        vmid = request.session['vmid']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/status/{command}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers, verify=False)
        name =  request.session['vmname']
        response = redirect('cloudservers')
        return response
    else:
        return redirect('cloudservers')

def notifications(request,id):
    if 'username' in request.session:
        name = request.session['username']
        client = Client.objects.get(api_name=name)
        notifications = Notification.objects.filter(receivers = client)
        notification = Notification.objects.get(id=id)
        context = {
            'notifications':notifications,
            'notification' : notification,
            'client' : client
        }
        return render(request,'notification.html',context)
    else:
        return redirect('login')

def helpdesk(request,id):
    if 'username' in request.session:
        if request.method == 'POST':
            subject = request.POST['subject']
            description = request.POST['description']
            category = request.POST['category']
            api_name = request.session['username']
            client = Client.objects.get(api_name=api_name)
            ticket = Ticket.objects.create(subject=subject,description=description,category=category,Client=client,status='open')
            ticket.save()
            return redirect('helpdesk',id=id)
        else:
            client = Client.objects.get(id=id)
            tickets = Ticket.objects.filter(Client=id).order_by('-id')
            context = {
                'client':client,
                'tickets':tickets
            }
            return render(request,'helpdesk.html',context)
    else:
        return redirect('login')

def edit_ticket(request,id):
    if request.method == 'POST':
        subject = request.POST['subject']
        description = request.POST['description']
        category = request.POST['category']
        ticket = Ticket.objects.get(id=id)
        ticket.subject=subject
        ticket.description=description
        ticket.category=category
        ticket.save()
        return redirect(edit_ticket,id=id)
    else:
        ticket = Ticket.objects.get(id=id)
        api_name = request.session['username']
        client = Client.objects.get(api_name=api_name)
        context = {
            'ticket':ticket,
            'client':client
        }
        return render(request,'edit_ticket.html',context)

def remove_ticket(request):
    if request.method=='POST':
        client_id = request.POST['clientid']
        ticket_id = request.POST['ticketid']
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.delete()
        return redirect('helpdesk',id=client_id)
    else:
        return redirect('cloudservers')

def firewall(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        vms = request.session['vms']
        csrf = request.session['csrf']
        for v in vms:
            if v['name'] == name:
                vm = v
        vmid = vm['vmid']
        node = vm['node']
        request.session['vmid'] = vm['vmid']
        request.session['vmname'] = vm['name']
        request.session['node']  = node
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/rules"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, verify=False)
        try:
            response_json = response.json()
            firewall = response_json['data']
        except:
            return redirect('logout')
            
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        request.session['firewall'] = firewall
        context={
                'vm':vm,
                'client':client,
                'notifications':notifications
            }
        response = render(request,'firewall.html',context)
        return response
    else:
        return redirect('login')

def addrule(request):
    if request.method == 'POST':
        iface = request.POST['iface']
        proto = request.POST['proto']
        macro = request.POST['macro']
        enable = request.POST.get('enable')
        if enable == 'on':
            enable = 1
        else:
            enable = 0
        source = request.POST['source']
        sport = request.POST['sport']
        dest = request.POST['dest']
        dport = request.POST['dport']

        action = 'ACCEPT'
        type = 'in'
        iface=str(iface)
        loglevel='nolog'

        if macro != '':
            params = {'iface':iface,'source':source,'dest':dest,'action':action,'type':type,'macro':macro,'enable':enable,'log':loglevel}
        else:
            params = {'iface':iface,'proto':proto,'source':source,'sport':sport,'dest':dest,'dport':dport,'action':action,'type':type,'macro':macro,'enable':enable,'log':loglevel}
        node = request.session['node']
        vmid= request.session['vmid']
        csrf = request.session['csrf']
        ticket = request.session['ticket']

        
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/rules"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params,verify=False)
        

        if response.status_code == 200:
            messages.warning(request,'Successfuly Added')
        else:
            messages.warning(request,response.content)
        response_json = response.json()
        vmname = request.session['vmname']
        return redirect('firewall',name=vmname)
    else:
        return redirect('login')

def edit_rule(request,id):
    if request.method == 'POST':
        iface = request.POST['iface']
        proto = request.POST['proto']
        macro = request.POST['macro']
        enable = request.POST.get('enable')
        if enable == 'on':
            enable = 1
        else:
            enable = 0
        source = request.POST['source']
        sport = request.POST['sport']
        dest = request.POST['dest']
        dport = request.POST['dport']

        action = 'ACCEPT'
        type = 'in'
        loglevel='nolog'

        pos = int(id)
        node = request.session['node']
        csrf = request.session['csrf']
        vmid = request.session['vmid']
        ticket = request.session['ticket']

        firewall = request.session['firewall']
        for fire in firewall:
            if fire['pos'] == id:
                firew=fire
        try:
            if firew['macro']:
                mselected = "true"
            else:
                mselected = "false"
        except:
            mselected = "false"
        if macro != '':
            params = {'iface':iface,'proto':'','source':source,'sport':'','dest':dest,'dport':'','action':action,'type':type,'macro':macro,'enable':enable,'log':loglevel}
        else:
             params = {'iface':iface,'proto':proto,'source':source,'sport':sport,'dest':dest,'dport':dport,'action':action,'type':type,'macro':macro,'enable':enable,'log':loglevel}
        
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/rules/{pos}"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.put(url,headers=headers,params=params,verify=False)
        if response.status_code == 200:
            messages.warning(request,'Successfuly Edited')
        else:
            messages.warning(request,response.content)
        vmname = request.session['vmname']
        return redirect('firewall',name=vmname)
    else:
        node = request.session['node']
        vmid= request.session['vmid']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        pos = int(id)
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/rules/{pos}"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers,verify=False)
        firewall = request.session['firewall']
        for fire in firewall:
            if fire['pos'] == id:
                firew=fire
        try:
            if firew['macro']:
                mselected = "true"
            else:
                mselected = "false"
        except:
            mselected = "false"
        
        context = {
            'firew':firew,
            'mselected':mselected
        }
        return render(request,'edit_rule.html',context)

def removerule(request):
    if request.method == 'POST':
        pos = request.POST['pos']
        digest = request.POST['digest']
        node = request.session['node']
        vmid= request.session['vmid']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        params={'digest':digest}
        url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/rules/{pos}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.delete(url,headers=headers,params=params, verify=False)
        vmname = request.session['vmname']
        return redirect('firewall',vmname)
    else:
        return redirect('cloudserversrr')
def logs(request):
    if 'username' in request.session:
        ticket = request.session['ticket']
        csrf = request.session['csrf']
        url = f"{BASE_URL}/api2/json/cluster/tasks"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, verify=False)
        
        try:
            response_json = response.json()
            logs = response_json['data']
            Logs =[]
            for log in logs:
                if ((log['type'] == 'qmrollback') or (log['type'] == 'qmrestore') or 
                    (log['type'] == 'vzdump') or (log['type'] == 'imgdel') or (log['type'] == 'qmsnapshot')
                    or (log['type'] == 'qmdelsnapshot')):
                    Logs.append(log)
                log['starttime']=str(date.fromtimestamp(log['starttime']))
                log['endtime']=str(date.fromtimestamp(log['endtime']))
                dict = {"vzdump":"Backup now","qmrestore":"Restore Backup","imgdel":"Remove backup","qmsnapshot":"Take snapshot","qmrollback":"Rollback snap",
                         "qmdelsnapshot":"Delete Snapshot"}
                if log['type'] in dict:
                    log['type'] = dict[log['type']]
            request.session['logs'] = Logs
        except:
            messages.warning(request,'undergoing tasks, please wait few seconds.')
            name = request.session['vmname']
            return redirect('backup',name=name)
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        context={
                'client':client,
                'notifications':notifications
            }
        return render(request,'logs.html',context)
    else:
        return redirect('logout')

def firewall_options(request,name):
    if 'username' in request.session:
            if request.method=='POST':
                firewall = request.POST['firewall']
                dhcp = request.POST['dhcp']
                macfilter = request.POST['macfilter']
                ipfilter = request.POST['ipfilter']
                inpolicy = request.POST['inpolicy']
                outpolicy = request.POST['outpolicy']
                if firewall == 'yes':
                    firewall = 1
                else:
                    firewall = 0
                if dhcp == 'no':
                    dhcp = 0
                else:
                    dhcp = 1
                if macfilter == 'yes':
                    macfilter = 1
                else:
                    macfilter = 0
                if ipfilter == 'yes':
                    ipfilter = 1
                else:
                    ipfilter = 0

                node = request.session['node']
                ticket = request.session['ticket']
                csrf = request.session['csrf']
                vmid = request.session['vmid']
                params = {'enable':firewall,'dhcp':dhcp,'ipfilter':ipfilter,'macfilter':macfilter,'policy_in':inpolicy,'policy_out':outpolicy}
                url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/options"
                headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
                try:
                    response = requests.put(url,headers=headers,params=params,verify=False)
                    response_json = response.json()
                    options = response_json['data']
                    context={
                        'options':options,
                        }
                except:
                    return redirect('logout')
                
                vmname = request.session['vmname']
                return redirect('firewall_options',name=vmname)
            else:
                node = request.session['node']
                csrf = request.session['csrf']
                vmid = request.session['vmid']
                ticket = request.session['ticket']
                url = f"{BASE_URL}/api2/json/nodes/{node}/qemu/{vmid}/firewall/options"
                headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
                response = requests.get(url,headers=headers, verify=False)
                try:
                    response_json = response.json()
                    context={
                        'options':response_json['data']
                    }
                except:
                    return redirect('logout')
                return render(request,'firewall_options.html',context)
    else:
        return redirect('login')


def changepassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        #confirm_password = request.POST['confirm_password']
        userid = request.session['username']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        params = {'password':password,"userid":userid}
        url = f"{BASE_URL}/api2/json/access/password"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.put(url,headers=headers, params=params, verify=False)
        if response.status_code == 200:
            messages.warning(request,'Successfuly Changed')
            return redirect('changepassword')
        else:
            messages.warning(request,json.loads(response.content)["errors"])
            return redirect('changepassword')
    else:
        if 'username' in request.session:
            return render(request,'changepassword.html')
        else:
            return redirect('logout')