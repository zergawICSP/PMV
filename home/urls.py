from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.cloudservers,name='cloudservers'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('console/<str:name>/',views.console,name='console'),
    path('summary/<str:name>/<str:timely>/',views.summary,name='summary'),
    path('editnotes',views.editnotes,name='editnotes'),
    path('backup/<str:name>/',views.backup,name='backup'),
    path('backupnow',views.backupnow,name='backupnow'),
    path('removebackup',views.removebackup,name='removebackup'),
    path('restorebackup',views.restorebackup,name='restorebackup'),
    path('snapshots/<str:name>/',views.snapshots,name='snapshots'),
    path('takesnapshot',views.takesnapshot,name='takesnapshot'),
    path('removesnap',views.removesnap,name='removesnap'),
    path('rollbacksnap',views.rollbacksnap,name='rollbacksnap'),
    path('firewall/<str:name>/',views.firewall,name='firewall'),
    path('addrule',views.addrule,name='addrule'),
    path('edit_rule/<int:id>/',views.edit_rule,name='edit_rule'),
    path('removerule',views.removerule,name='removerule'),
    path('firewall_options/<str:name>/',views.firewall_options,name='firewall_options'),
    path('cloudservers',views.cloudservers,name='cloudservers'),
    path('vmstatus',views.vmstatus,name='vmstatus'),
    path('notifications/<str:id>/',views.notifications,name='notifications'),
    path('helpdesk/<str:id>/',views.helpdesk,name='helpdesk'),
    path('edit_ticket/<str:id>/',views.edit_ticket,name='edit_ticket'),
    path('remove_ticket',views.remove_ticket,name='remove_ticket'),
    path('logs',views.logs,name='logs'),
    path('changepassword',views.changepassword,name='changepassword')
]
