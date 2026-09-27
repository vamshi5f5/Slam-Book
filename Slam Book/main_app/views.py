import gspread
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index_page(request):
    return render(request, 'main_app/index.html')

def register_page(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        cp_word = request.POST.get('confirm_password')

        if p_word != cp_word:
            messages.error(request, "Passwords do not match!")
            return redirect('register')
        if User.objects.filter(username=u_name).exists():
            messages.info(request, "Username taken. Try logging in!")
            return redirect('login')

        User.objects.create_user(username=u_name, password=p_word)
        return redirect('login')
    return render(request, 'main_app/register.html')

def login_page(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid credentials.")
    return render(request, 'main_app/login.html')

def dashboard_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    my_slams = []
    
    # READ FROM GOOGLE SHEETS
    try:
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open("slam book")
        worksheet = sh.get_worksheet(0)
        
        # Get all data from the sheet
        all_data = worksheet.get_all_values()
        
        # Loop through rows (skipping the first row assuming it's headers)
        for row in all_data[1:]:
            # Check if the row has at least 7 columns (to support older entries)
            if len(row) >= 7 and row[0] == request.user.username:
                my_slams.append({
                    'name': row[1],
                    'phone_number': row[2], # Changed key to 'phone_number' to match HTML
                    'gender': row[3],
                    'description': row[4],
                    'memory': row[5],
                    'one_line': row[6],
                    # Safely grab the 'feeling' field ONLY if it exists (Index 7)
                    # This prevents older entries from crashing your dashboard!
                    'feeling': row[7] if len(row) >= 8 else "N/A" 
                })
    except Exception as e:
        print(f"Error reading from sheet: {e}")

    # Reverse the list so the newest slams appear at the top
    my_slams.reverse()
    
    share_link = request.build_absolute_uri(f'/write/{request.user.username}/')
    
    return render(request, 'main_app/dashboard.html', {
        'slams': my_slams,
        'share_link': share_link
    })

def slam_page(request, username):
    owner = get_object_or_404(User, username=username)
    return render(request, 'main_app/slam.html', {'owner': owner})

def submit_slam(request, username):
    if request.method == "POST":
        f_name = request.POST.get('name', '')
        f_phone = request.POST.get('phone_number', '')
        f_gender = request.POST.get('gender', '')
        f_desc = request.POST.get('description', '')
        f_memory = request.POST.get('memory', '')
        f_one_line = request.POST.get('one_line', '')
        
        # NEW: Grab the feeling field from the form
        f_feeling = request.POST.get('feeling', '') 

        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open("slam book")
        worksheet = sh.get_worksheet(0)
        
        # NEW: Added f_feeling to the END of the row. 
        # Putting it at the end ensures we don't mess up the order of older data in your sheet.
        full_row = [
            username, f_name, f_phone, f_gender, f_desc, f_memory, f_one_line, f_feeling
        ]
        worksheet.append_row(full_row)

        return render(request, 'main_app/index.html') 
    return redirect('index')

def logout_user(request):
    logout(request)
    return redirect('login')