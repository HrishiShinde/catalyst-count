# upload/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import File, Company
from .forms import QueryForm
import os
import pandas as pd
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import UserForm

def upload_page(request):
    if request.method == 'POST':
        # deletes existing data.
        delete_data()

        file = request.FILES['file'].read()
        fileName= request.POST['filename']
        existingPath = request.POST['existingPath']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']
        filesize = request.POST['filesize']

        if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="":
            res = JsonResponse({'data':'Invalid Request'})
            return res
        else:
            if existingPath == 'null':
                path = 'media/' + fileName
                with open(path, 'wb+') as destination: 
                    destination.write(file)
                FileFolder = File()
                FileFolder.existingPath = fileName
                FileFolder.eof = end
                FileFolder.name = fileName
                FileFolder.save()
                if int(end):
                    res = JsonResponse({'data':'Uploaded Successfully','existingPath': fileName})
                else:
                    res = JsonResponse({'existingPath': fileName})
                return res
            else:
                path = 'media/' + existingPath
                model_id = File.objects.get(existingPath=existingPath)
                if model_id.name == fileName:
                    if not model_id.eof:
                        with open(path, 'ab+') as destination: 
                            destination.write(file)
                        if int(end):
                            model_id.eof = int(end)
                            model_id.save()
                            upload_filesize = os.path.getsize(path)
                            if int(upload_filesize) == int(filesize):
                                upload_file_data(path)
                            res = JsonResponse({'data' : 'Uploaded Successfully', 'existingPath' : model_id.existingPath})
                        else:
                            res = JsonResponse({'existingPath':model_id.existingPath})    
                        return res
                    else:
                        res = JsonResponse({'data':'EOF found. Invalid request'})
                        return res
                else:
                    res = JsonResponse({'data':'No such file exists in the existingPath'})
                    return res
    return render(request, 'upload.html')

def query_builder(request):
    form = QueryForm(request.GET or None)
    companies = Company.objects.all()
    
    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        industry = form.cleaned_data.get('industry')
        year_founded = form.cleaned_data.get('year_founded')
        city = form.cleaned_data.get('city')
        state = form.cleaned_data.get('state')
        country = form.cleaned_data.get('country')
        employees_from = form.cleaned_data.get('employees_from')
        employees_to = form.cleaned_data.get('employees_to')

        if keyword and keyword != "":
            companies = companies.filter(
                Q(name__icontains=keyword) |
                Q(domain__icontains=keyword) |
                Q(year_founded__icontains=keyword) |
                Q(industry__icontains=keyword) |
                Q(size_range__icontains=keyword) |
                Q(city__icontains=keyword) |
                Q(state__icontains=keyword) |
                Q(country__icontains=keyword) |
                Q(linkedin_url__icontains=keyword) |
                Q(current_employee_estimate__icontains=keyword) |
                Q(total_employee_estimate__icontains=keyword)
            )
        if industry and industry != "":
            companies = companies.filter(industry=industry)
        if year_founded and year_founded != "":
            companies = companies.filter(year_founded=year_founded)
        if city and city != "":
            companies = companies.filter(city=city)
        if state and state != "":
            companies = companies.filter(state=state)
        if country and country != "":
            companies = companies.filter(country=country)
        if employees_from and employees_from != "":
            companies = companies.filter(
                Q(current_employee_estimate__gte=employees_from) 
            )
        if employees_to and employees_to != "":
            companies = companies.filter(
                Q(current_employee_estimate__lte=employees_to)
            )
    count = companies.count()
    return render(request, 'query_builder.html', {'form': form, 'count': count})

def upload_file_data(file_path):
    if file_path:
        chunk_size = 10000

        for chunk in pd.read_csv(file_path, chunksize=chunk_size, delimiter=';', quoting=3, header=None, skiprows=1, on_bad_lines='skip'):
            instances = []
            for _, row in chunk.iterrows():
                raw_row = row.tolist()[0]
                row = parse_row(raw_row)
                locality = get_idx(row, 6)
                locality = parse_locality(locality)
                instance = Company(
                    name= get_idx(row, 1),
                    domain= get_idx(row, 2),
                    year_founded= get_idx(row, 3),
                    industry= get_idx(row, 4),
                    size_range= get_idx(row, 5),
                    city= locality.get('city'),
                    state= locality.get('state'),
                    country= get_idx(row, 7),
                    linkedin_url= get_idx(row, 8),
                    current_employee_estimate= get_idx(row, 9),
                    total_employee_estimate= get_idx(row, 10),
                )
                instances.append(instance)

            with transaction.atomic():
                Company.objects.bulk_create(instances, ignore_conflicts=True)

def parse_row(row):
    row_list = []
    i = 0
    inside_quotes = False
    current_field = []

    while i < len(row):
        if row[i] == '"':
            if inside_quotes and i + 1 < len(row) and row[i + 1] == '"':
                current_field.append('"')
                i += 1
            else:
                inside_quotes = not inside_quotes
        elif row[i] == ',' and not inside_quotes:
            row_list.append(''.join(current_field).strip())
            current_field = []
        else:
            current_field.append(row[i])
        i += 1
    
    row_list.append(''.join(current_field).strip())
    
    return row_list

def parse_locality(locality):
    parts = [part.strip() for part in locality.split(',')]
    
    location_dict = {'city': None, 'state': None, 'country': None}

    if len(parts) == 3:
        location_dict['city'], location_dict['state'], location_dict['country'] = parts
    elif len(parts) == 2:
        location_dict['city'], location_dict['state'] = parts
    elif len(parts) == 1:
        location_dict['city'] = parts[0]
    
    return location_dict

def get_idx(lst, index):
    if 0 <= index < len(lst):
        return lst[index]
    else:
        return ""

def users(request, add=False):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users, "new_add": add})

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            return users(request, True)
    return render(request, 'add_user.html')

def delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect('users')

def delete_data(request):
    Company.objects.all().delete()
    File.objects.all().delete()
    return JsonResponse({'message': 'Data deleted successfully'})

