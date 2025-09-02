from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest
from .forms import LeaveRequestForm
from django.views.generic import UpdateView, DeleteView, CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Home page
@login_required
def home(request):
    total_leaves = request.user.leaverequest_set.count()
    approved_leaves = request.user.leaverequest_set.filter(status='Approved').count()
    pending_leaves = request.user.leaverequest_set.filter(status='Pending').count()
    
    context = {
        'total_leaves': total_leaves,
        'approved_leaves': approved_leaves,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'leaves/home.html', context)


# Employee: My Leaves
@login_required
def my_leaves(request):
    leaves = LeaveRequest.objects.filter(employee=request.user)
    return render(request, 'leaves/my_leaves.html', {'leaves': leaves})


# Employee: Create Leave (Function-based view)
@login_required
def create_leave(request):
    if request.user.is_superuser:
        return redirect('home')  # superuser cannot create
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            return redirect('my-leaves')
    else:
        form = LeaveRequestForm()
    return render(request, 'leaves/leave_form.html', {'form': form})


# Superuser / Staff: View all leaves (Function-based view)
@login_required
def all_leaves_hr(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('home')
    if request.user.is_staff:
        leaves = LeaveRequest.objects.filter(employee__is_staff=False)
    else:
        leaves = LeaveRequest.objects.all()
    return render(request, 'leaves/all_leaves_hr.html', {'leaves': leaves})


# CBV version of AllLeavesHRView
class AllLeavesHRView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LeaveRequest
    template_name = 'leaves/all_leaves_hr.html'
    context_object_name = 'leaves'

    def get_queryset(self):
        if self.request.user.is_staff:
            return LeaveRequest.objects.filter(employee__is_staff=False)
        elif self.request.user.is_superuser:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.none()

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# Approve / Reject Leave
@login_required
def approve_reject_leave(request, pk, action):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.user.is_staff and leave.employee.is_staff:
        return redirect('all-leaves-hr')
    if action == 'approve':
        leave.status = 'Approved'
    elif action == 'reject':
        leave.status = 'Rejected'
    leave.save()
    return redirect('all-leaves-hr')


# Superuser delete leave (Function-based)
@login_required
def delete_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.user.is_superuser:
        leave.delete()
    return redirect('all-leaves-hr')


# CBV: Update Leave
class LeaveUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leaves/leave_form.html'
    success_url = reverse_lazy('my-leaves')

    def test_func(self):
        leave = self.get_object()
        return self.request.user == leave.employee


# CBV: Create Leave
class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leaves/leave_form.html'
    success_url = reverse_lazy('my-leaves')

    def form_valid(self, form):
        form.instance.employee = self.request.user
        return super().form_valid(form)


# CBV: Delete Leave (Superuser only)
class LeaveDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = LeaveRequest
    template_name = 'leaves/leave_confirm_delete.html'
    success_url = reverse_lazy('all-leaves-hr')

    def test_func(self):
        leave = self.get_object()
        return self.request.user.is_superuser
