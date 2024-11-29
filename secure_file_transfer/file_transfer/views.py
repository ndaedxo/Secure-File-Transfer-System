# secure_file_transfer\file_transfer\views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FileTransfer
from .forms import FileUploadForm
from .encryption import FileEncryptor
import base64
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def dashboard(request):
    upload_history = FileTransfer.objects.filter(
        user=request.user, 
        transfer_type='upload'
    ).order_by('-created_at')
    
    download_history = FileTransfer.objects.filter(
        user=request.user, 
        transfer_type='download'
    ).order_by('-created_at')
    
    transfers = FileTransfer.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'file_transfer/dashboard.html', {
        'upload_history': upload_history,
        'download_history': download_history,
        'transfers': transfers,
    })


@login_required
def upload_file(request):
    """
    Handle file upload with encryption
    """
    upload_progress = 0  # Initialize a default value for upload progress

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the uploaded file
                uploaded_file = request.FILES['file']

                # Encrypt the file
                encryption_result = FileEncryptor.encrypt_file(
                    uploaded_file, 
                    request.user.username  # Using username as password (replace with more secure method)
                )
                
                # Save encrypted file
                file_transfer = FileTransfer.objects.create(
                    user=request.user,
                    filename=uploaded_file.name,
                    transfer_type='upload',
                    file=uploaded_file,
                    salt=encryption_result['salt'],
                    status='completed'
                )
                
                messages.success(request, 'File uploaded and encrypted successfully!')
                return redirect('dashboard')
            
            except Exception as e:
                messages.error(request, f'Upload failed: {str(e)}')

    else:
        form = FileUploadForm()
    
    # Pass upload_progress to the template
    return render(request, 'file_transfer/upload.html', {'form': form, 'upload_progress': upload_progress})

@login_required
def download_file(request, file_id):
    """
    Handle file download with decryption
    """
    try:
        file_transfer = FileTransfer.objects.get(
            id=file_id, 
            user=request.user
        )
        
        # Decrypt the file
        decrypted_contents = FileEncryptor.decrypt_file(
            file_transfer.file.read(),
            request.user.username,  # Use username as password (replace with more secure method)
            base64.b64decode(file_transfer.salt)
        )
        
        # Update transfer history
        file_transfer.transfer_type = 'download'
        file_transfer.status = 'completed'
        file_transfer.save()
        
        # Prepare file response
        response = HttpResponse(
            decrypted_contents, 
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_transfer.filename}"'
        return response
    
    except Exception as e:
        messages.error(request, f'Download failed: {str(e)}')
        return redirect('dashboard')
    


def login_view(request):
    """
    Handle user login
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'file_transfer/login.html')

def signup_view(request):
    """
    Handle user registration
    """
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords don't match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully. You can log in now.')
            return redirect('login')  # Redirect to login page
    
    return render(request, 'file_transfer/signup.html')

def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    return redirect('login')