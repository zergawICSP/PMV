from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('',views.cloudservers,name='cloudservers'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('console/<str:name>/',views.console,name='console'),
    path('summary/<str:name>/',views.summary,name='summary'),
    path('backup/<str:name>/',views.backup,name='backup'),
    path('backupnow',views.backupnow,name='backupnow'),
    path('removebackup',views.removebackup,name='removebackup'),
    path('restorebackup',views.restorebackup,name='restorebackup'),
    path('snapshots/<str:name>/',views.snapshots,name='snapshots'),
    path('takesnapshot',views.takesnapshot,name='takesnapshot'),
    path('removesnap',views.removesnap,name='removesnap'),
    path('rollbacksnap',views.rollbacksnap,name='rollbacksnap'),
    path('cloudservers',views.cloudservers,name='cloudservers'),
    path('vmstatus',views.vmstatus,name='vmstatus'),
    path('notifications/<str:id>/',views.notifications,name='notifications'),
]
