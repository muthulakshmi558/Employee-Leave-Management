from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my-leaves/', views.my_leaves, name='my-leaves'),
    path('create/', views.LeaveCreateView.as_view(), name='leave-create'),
    path('<int:pk>/update/', views.LeaveUpdateView.as_view(), name='leave-update'),
    path('<int:pk>/delete/', views.LeaveDeleteView.as_view(), name='leave-delete'),
    path('hr/leaves/', views.all_leaves_hr, name='all-leaves-hr'),  # ← use function-based view
    path('<int:pk>/<str:action>/', views.approve_reject_leave, name='approve-reject-leave'),
]