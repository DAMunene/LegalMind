from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserLoginForm, ContractUploadForm, ContractSearchForm
from .models import Contract
from .services import ContractAnalyzer

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('contracts')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
            form = UserLoginForm()
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = UserLoginForm()
        return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

def contract_list(request):
    search_form = ContractSearchForm(request.GET)
    
    if request.user.is_authenticated:
        contracts = Contract.objects.filter(user=request.user)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']
            risk_level = request.GET.get('risk_level')
            
            if search_query:
                contracts = contracts.filter(Q(title__icontains=search_query))
            
            if risk_level:
                if risk_level == 'high':
                    contracts = contracts.filter(riskanalysis__risk_score__gte=70)
                elif risk_level == 'medium':
                    contracts = contracts.filter(riskanalysis__risk_score__range=(30, 69))
                elif risk_level == 'low':
                    contracts = contracts.filter(riskanalysis__risk_score__range=(0, 29))
    else:
        contracts = Contract.objects.none()  # Return empty queryset for unauthenticated users
    
    return render(request, 'contracts/list.html', {
        'contracts': contracts,
        'search_form': search_form
    })

@login_required
def contract_upload(request):
    if request.method == 'POST':
        form = ContractUploadForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.user = request.user
            contract.save()
            
            # Analyze the contract
            analyzer = ContractAnalyzer()
            risk_analysis = analyzer.analyze_contract(contract)
            
            # Store the analysis results
            risk_analysis.save()
            
            messages.success(request, 'Contract uploaded and analyzed successfully!')
            return redirect('contract-detail', pk=contract.pk)
    else:
        form = ContractUploadForm()
    return render(request, 'contracts/upload.html', {'form': form})

@login_required
def contract_detail(request, pk):
    contract = Contract.objects.get(pk=pk, user=request.user)
    try:
        risk_analysis = contract.riskanalysis  # Django automatically creates related_name as lowercase model name
    except RiskAnalysis.DoesNotExist:
        risk_analysis = None
    
    # Get file extension
    file_extension = contract.file.name.split('.')[-1].upper() if '.' in contract.file.name else ''
    
    return render(request, 'contracts/detail.html', {
        'contract': contract,
        'risk_analysis': risk_analysis,
        'file_extension': file_extension
    })

@login_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ContractUploadForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            contract = form.save()
            messages.success(request, 'Contract updated successfully!')
            return redirect('contract-detail', pk=contract.pk)
    else:
        form = ContractUploadForm(instance=contract)
    return render(request, 'contracts/upload.html', {
        'form': form,
        'edit_mode': True
    })

@login_required
def contract_download(request, pk):
    contract = get_object_or_404(Contract, pk=pk, user=request.user)
    response = FileResponse(contract.file, as_attachment=True)
    return response

@login_required
@require_POST
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk, user=request.user)
    contract.delete()
    messages.success(request, 'Contract deleted successfully!')
    return redirect('contracts')
