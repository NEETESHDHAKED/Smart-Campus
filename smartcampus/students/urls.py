from django.urls import path
from . import views
urlpatterns = [
    path('',views.login_view,name='root'),
    path('home/', views.home, name='home'),
    path('add/', views.add_student, name='add'),
    path('attendance/<str:roll>/', views.mark_attendance, name='att'),
    path('login/',views.login_view,name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('face/', views.face_verify, name='face'),
    path('list/', views.attendance_list, name='list'),

]
