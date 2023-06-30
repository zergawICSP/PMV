from django.db import models

# Create your models here.
class Client(models.Model):
    company_name = models.CharField(max_length=300)
    api_name = models.CharField(max_length=300,null=True,blank=True)
    phonenumber = models.CharField(max_length=300)
    phonenumber2 = models.CharField(max_length=300,blank=True,null=True)
    address = models.CharField(max_length=300,)
    email = models.EmailField(max_length=300) 
    website = models.CharField(max_length=300)
    logo = models.ImageField(upload_to ='uploads/clients/')
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
    