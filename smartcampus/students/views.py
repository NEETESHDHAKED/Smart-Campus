from django.shortcuts import render, redirect
from .models import Student, Attendance
from datetime import date
import qrcode
import base64
from io import BytesIO
import math

COLLEGE_LAT = 26.7819
COLLEGE_LON = 75.8218
ALLOWED_DISTANCE = 0.3

def distance_km(lat1,lon1,lat2,lon2):
    R = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(a))


def home(request):
    if 'roll' not in request.session:
        return redirect('login')
    roll = request.session.get('roll')
    search = request.GET.get('search','')

    if roll == 'admin':
        is_admin = True
        if search:
            students = Student.objects.filter(name__icontains=search) 
        else:
            students = Student.objects.all()
    else:
        is_admin = False
        students = Student.objects.filter(roll=roll)
    for s in students:
        qr = qrcode.make(f"http://192.168.1.48:8000/attendance/{s.roll}/")
        buffer = BytesIO()
        qr.save(buffer,format='PNG')
        s.qr_code = base64.b64encode(buffer.getvalue()).decode()
    name = request.session.get('name')   
    return render(request, 'home.html', {'students': students,'name':name,'roll':roll,'is_admin': is_admin})

def add_student(request):
    if request.method == 'POST':
        Student.objects.create(
            name=request.POST['name'],
            roll=request.POST['roll'],
            branch=request.POST['branch'],
            phone=request.POST['phone']
        )
        return redirect('home')
    return render(request, 'add_student.html')

def mark_attendance(request, roll):
    device_id = request.COOKIES.get('device_id')
    if not device_id:
        import uuid
        device_id = str(uuid.uuid4())
    student = Student.objects.get(roll=roll)
    login_roll = request.session.get('roll')

    if login_roll == 'admin':
        students = Student.objects.all()
    else:
        students = Student.objects.filter(roll=login_roll)
    
    today = date.today()

    if request.method == 'POST':
        face_photo = request.POST.get('face_photo')
        if not face_photo:
            res = render(request,'home.html',{'students':students,'msg':'Pehle Face Photo Khicho! 📸'})
            res.set_cookie('device_id',device_id)
            return res

        try:
            lat = float(request.POST.get('latitude') or 0)
            lon = float(request.POST.get('longitude') or 0)
        except:
            lat, lon = 0, 0
        if lat == 0:
            res = render(request,'home.html',{'students':students,'msg':'Location ON Karo! 📍'})
            res.set_cookie('device_id',device_id)
            return res

        dist = distance_km(COLLEGE_LAT, COLLEGE_LON, lat, lon)
        if dist > ALLOWED_DISTANCE:
            res = render(request,'home.html',{'students':students,'msg':f'College se bahar ho! {dist:.2f} KM dur ho'})
            res.set_cookie('device_id',device_id)
            return res

        if Attendance.objects.filter(student=student,date=today).exists():
            res = render(request,'home.html',{'students':students,'msg':'Pehle se present hai!'})
            res.set_cookie('device_id',device_id)
            return res

        if Attendance.objects.filter(device_id=device_id,date=today).exists():
            res = render(request,'home.html',{'students':students,'msg':'No Proxy! Ek phone se ek hi'})
            res.set_cookie('device_id',device_id)
            return res

        Attendance.objects.create(student=student, device_id=device_id, date=today, latitude=lat, longitude=lon, face_photo=face_photo)
        res = render(request,'home.html',{'students':students,'msg':'Attendance Lag Gayi! ✅'})
        res.set_cookie('device_id',device_id)
        return res

    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        roll = request.POST.get('roll')
        try:
            student = Student.objects.get(roll=roll,password=request.POST.get('password'))
            request.session['roll'] = roll
            request.session['name'] = student.name
            return redirect('home')
        except:
            return render(request,'login.html',{'error':'Roll No. nhi mila'})
    return render(request,'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')

def attendance_list(request):
    students = Student.objects.all()
    return render(request,'attendance_list.html',{'students':students})

def face_verify(request):
    return render(request,'face_verify.html')
