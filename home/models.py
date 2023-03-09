from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Client(models.Model):
    company_name = models.CharField(max_length=300)
    api_name = models.CharField(max_length=300,default='apiclient')
    phonenumber = models.CharField(max_length=300)
    phonenumber2 = models.CharField(max_length=300,blank=True,null=True)
    address = models.CharField(max_length=300,blank=True,null=True)
    email = models.EmailField(max_length=300,blank=True,null=True) 
    website = models.CharField(max_length=300,blank=True,null=True)
    logo = models.ImageField(upload_to ='uploads/clients/',blank=True,null=True)
    buyingdate = models.DateField()

    def __str__(self):
        return self.company_name
    
class Notification(models.Model):
    heading1 = models.CharField(max_length=300)
    heading2 = models.CharField(max_length=300,null=True,blank=True)
    message = models.TextField()
    receivers = models.ManyToManyField(Client,related_name='receiver')

    def __str__(self):
        return self.heading1

class Notes(models.Model):
    vmid = models.CharField(max_length=300,null=True,blank=True)
    notes = models.TextField()
    note_by = models.ManyToManyField(Client,related_name='clients')

    def __str__(self):
        return self.vmid

class Ticket(models.Model):
    subject = models.CharField(max_length=300,null=True,blank=True)
    description = models.TextField()
    category = models.CharField(max_length=300,null=True,blank=True)
    status = models.CharField(max_length=300,null=True,blank=True)
    assigned_person = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    Client = models.ForeignKey(Client,on_delete=models.CASCADE)

    def __str__(self):
        return self.subject