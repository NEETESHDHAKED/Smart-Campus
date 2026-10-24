from django.db import models
class Student(models.Model):
    name = models.CharField(max_length=100)
    roll = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=20, default=1234)
    qr_code = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    device_id = models.CharField(max_length=100,blank=True)
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    face_photo = models.TextField(null=True,blank=True)
    

    def __str__(self):
        return f"{self.student.name} - {self.date}"    
