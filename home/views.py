import datetime
from django.http import HttpResponse
from django.shortcuts import render,redirect
import requests
from django.contrib import messages 
import urllib.parse
from .models import Client,Notification
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
        try:
            url = "https://10.0.201.30:8006/api2/json/access/ticket"
            headers = {"content-Type": "application/x-www-form-urlencoded"}
            response1 = requests.post(url, headers=headers, data=f"username={username}&password={password}", verify=False)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('login')

        if response1.status_code == 200:
            response_json = response1.json()
            username= response_json['data']['username']
            ticket = response_json['data']['ticket']
            csrf = response_json['data']['CSRFPreventionToken']

            url2 = "https://10.0.201.30:8006/api2/json/nodes"
            headers2 = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
            response2 = requests.get(url2,headers=headers2,verify=False)
            response_json = response2.json()
            nodes = response_json['data']
            for i in nodes:
                node=i
                break
            node = node['node']

            request.session['username'] = username
            request.session['ticket'] = ticket
            request.session['csrf'] = csrf
            request.session['nodes'] = nodes
            request.session['node'] = node

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

def fun(request):
    ticket = request.session['ticket']
    context={
            'ticket':ticket
        }
    return render(request,'fun.html',context)

def cloudservers(request):
    if 'username' in request.session:
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        node = request.session['node']

        try:
            url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu/"
            headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
            response = requests.get(url,headers=headers, verify=False)

            url = f"https://10.0.201.30:8006/api2/json/cluster/tasks"
            headers2 = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
            response2 = requests.get(url,headers=headers, verify=False)
        except:
            messages.error(request,'Invalid Credentials')
            return redirect('login')
        try:
            response_json = response.json()
            response_json2 = response2.json()
        except:
            return redirect('logout')
        print('response_json')
        print(response_json)
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')

        vms = response_json['data']
        tasks = response_json2['data']
        request.session['tasks'] = tasks
        for vm in vms:
            vm['uptime'] = str(datetime.timedelta(seconds=vm['uptime']))
        
        request.session['vms'] = vms
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
        print('vmid')
        print(vmname)
        url = "https://prxlag01node01.zergaw.com:5101/?console=kvm&novnc=1&vmid=" + str(vmid)+ "&vmname="+ str(vmname)+"&node="+node + "&resize=off&cmd="     
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
        response.set_cookie('PVEAuthCookie',ticket,domain='zergaw.com',secure=True)
        return response
    else:
        return redirect('login')

def summary(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        vms = request.session['vms']
        for vm in vms:
            if vm['name'] == name:
                vms = vm
        request.session['vmid'] = vms['vmid']
        request.session['vmname'] = vms['name']
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
        context={
                'ticket':ticket,
                'vm':vms,
                'client':client,
                'notifications':notifications
            }
        response = render(request,'summary.html',context)
        return response
    else:
        return redirect('login')

def snapshots(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        csrf = request.session['csrf']
        node = request.session['node']
        vms = request.session['vms']
        for vm in vms:
            if vm['name'] == name:
                vms = vm
        vmid = vms['vmid']
        request.session['vmid'] = vms['vmid']
        request.session['vmname'] = vms['name']
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu/{vmid}/snapshot"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, verify=False)
        response_json = response.json()

        snapshots = response_json['data']
        api_name = request.session['username']
        try:
            client = Client.objects.get(api_name=api_name)
            notifications = Notification.objects.filter(receivers = client)
        except:
            messages.error(request,'Please Contact Adminstrators')
            return redirect('logout')
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
        node = request.session['node']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        vmid = request.session['vmid']
        params = {'snapname':name,'description':description,'node':node,'vmid':vmid}
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu/{vmid}/snapshot"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params, verify=False)
        print('response.reason')
        print(response.reason)
        print(response.status_code)
        vmname = request.session['vmname']
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
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu/{vmid}/snapshot/{snapname}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.delete(url,headers=headers, verify=False)
        print('response.reason')
        print(response.reason)
        print(response.status_code)
        vmname = request.session['vmname']
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
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/rollback"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers, verify=False)
        print('response.reason')
        print(response.reason)
        print(response.status_code)
        vmname = request.session['vmname']
        return redirect('cloudservers')
    else:
        return redirect('cloudservers')

def backup(request,name):
    if 'username' in request.session:
        ticket = request.session['ticket']
        csrf = request.session['csrf']
        vms = request.session['vms']
        node = request.session['node']
        storage = 'local'
        
        vms = request.session['vms']
        for vm in vms:
            if vm['name'] == name:
                vms = vm
                print(vms)
        request.session['vmid'] = vms['vmid']
        request.session['vmname'] = vms['name']
        vmid = vms['vmid']
        params = {'vmid': vmid}
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/storage/{storage}/content/"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.get(url,headers=headers, params=params,verify=False)
        try:
            response_json = response.json()
        except:
            return redirect('logout')

        backups = response_json['data']
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
                'notifications':notifications
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
        storage = 'local'

        notes = request.POST.get('notes')
        if notes== '':
            notes = request.session['node']
        vmid = request.session['vmid']

        params = {'vmid': vmid,'notes-template':notes,'storage':storage,'compress':'zstd','mode':'snapshot'}
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/vzdump/"
        headers = {"CSRFPreventionToken": csrf, "Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params, verify=False)
        response_json = response.json()

        print(response_json)
        name =  request.session['vmname']
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
        storage = 'local'
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/storage/{storage}/content/{volid}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.delete(url,headers=headers,verify=False)
        print('response')
        print(response.status_code)
        print(response.reason)
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
        params={'vmid':vmid,'archive':volid}
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers,params=params, verify=False)
        print('response')
        print(response.status_code)
        print(response.reason)
        name =  request.session['vmname']
        response = redirect('backup',name)
        return response
    else:
        return redirect('cloudservers')

def vmstatus(request):
    if request.method == 'POST':
        command = request.POST['command']
        print(command)
        node = request.session['node']
        vmid = request.session['vmid']
        csrf = request.session['csrf']
        ticket = request.session['ticket']
        url = f"https://10.0.201.30:8006/api2/json/nodes/{node}/qemu/{vmid}/status/{command}"
        headers = {"CSRFPreventionToken": csrf,"Cookie": "PVEAuthCookie="+ticket}
        response = requests.post(url,headers=headers, verify=False)
        print('response from reboot ###############')
        print(response.status_code)
        print(response.reason)
        print(response.content)
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