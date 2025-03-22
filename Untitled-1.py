# polling_results/models.py
from django.db import models

class State(models.Model):
    state_id = models.IntegerField(primary_key=True)
    state_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.state_name

class LGA(models.Model):
    lga_id = models.IntegerField(primary_key=True)
    lga_name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.lga_name

class Ward(models.Model):
    ward_id = models.IntegerField(primary_key=True)
    ward_name = models.CharField(max_length=100)
    lga = models.ForeignKey(LGA, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.ward_name

class PollingUnit(models.Model):
    polling_unit_id = models.IntegerField(primary_key=True)
    polling_unit_name = models.CharField(max_length=100)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.polling_unit_name

class Party(models.Model):
    party_id = models.IntegerField(primary_key=True)
    party_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.party_name

class AnnouncedPuResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    polling_unit = models.ForeignKey(PollingUnit, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    party_score = models.IntegerField()
    
    class Meta:
        unique_together = ('polling_unit', 'party')
    
    def __str__(self):
        return f"{self.polling_unit} - {self.party}: {self.party_score}"

class AnnouncedLgaResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    lga = models.ForeignKey(LGA, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    party_score = models.IntegerField()
    
    class Meta:
        unique_together = ('lga', 'party')
    
    def __str__(self):
        return f"{self.lga} - {self.party}: {self.party_score}"

# Now let's create the views for each of the required tasks

# polling_results/views.py
from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import PollingUnit, LGA, Party, AnnouncedPuResult, AnnouncedLgaResult
from django import forms

# Question 1: Display result for any individual polling unit
def polling_unit_result(request):
    polling_units = PollingUnit.objects.all()
    results = None
    
    if request.method == 'GET' and 'polling_unit' in request.GET:
        polling_unit_id = request.GET.get('polling_unit')
        if polling_unit_id:
            results = AnnouncedPuResult.objects.filter(polling_unit_id=polling_unit_id)
    
    return render(request, 'polling_results/polling_unit_result.html', {
        'polling_units': polling_units,
        'results': results
    })

# Question 2: Display summed total result for all polling units under a particular LGA
def lga_result(request):
    lgas = LGA.objects.all()
    summed_results = None
    selected_lga = None
    
    if request.method == 'GET' and 'lga' in request.GET:
        lga_id = request.GET.get('lga')
        if lga_id:
            selected_lga = LGA.objects.get(pk=lga_id)
            # Get all polling units in this LGA
            polling_units_in_lga = PollingUnit.objects.filter(ward__lga_id=lga_id)
            
            # Get summed results for each party across these polling units
            summed_results = AnnouncedPuResult.objects.filter(
                polling_unit__in=polling_units_in_lga
            ).values('party__party_name').annotate(
                total_score=Sum('party_score')
            ).order_by('-total_score')
    
    return render(request, 'polling_results/lga_result.html', {
        'lgas': lgas,
        'summed_results': summed_results,
        'selected_lga': selected_lga
    })

# Question 3: Store results for ALL parties for a new polling unit
class NewResultForm(forms.Form):
    polling_unit_name = forms.CharField(max_length=100)
    ward = forms.ModelChoiceField(queryset=Ward.objects.all())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add fields for each party
        parties = Party.objects.all()
        for party in parties:
            self.fields[f'party_{party.party_id}'] = forms.IntegerField(
                label=f'{party.party_name} Score',
                min_value=0,
                initial=0
            )

def new_polling_unit_result(request):
    if request.method == 'POST':
        form = NewResultForm(request.POST)
        if form.is_valid():
            # Create new polling unit
            new_unit = PollingUnit.objects.create(
                polling_unit_name=form.cleaned_data['polling_unit_name'],
                ward=form.cleaned_data['ward'],
                # Generate a new unique ID
                polling_unit_id=PollingUnit.objects.order_by('-polling_unit_id').first().polling_unit_id + 1
            )
            
            # Save results for each party
            parties = Party.objects.all()
            for party in parties:
                party_score = form.cleaned_data[f'party_{party.party_id}']
                if party_score > 0:  # Only create records for parties with scores
                    AnnouncedPuResult.objects.create(
                        polling_unit=new_unit,
                        party=party,
                        party_score=party_score
                    )
            
            return redirect('polling_unit_result')
    else:
        form = NewResultForm()
    
    return render(request, 'polling_results/new_polling_unit.html', {
        'form': form,
        'parties': Party.objects.all()
    })

# polling_results/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('polling-unit/', views.polling_unit_result, name='polling_unit_result'),
    path('lga-result/', views.lga_result, name='lga_result'),
    path('new-result/', views.new_polling_unit_result, name='new_polling_unit_result'),
]

# Now let's create templates for each view

# polling_results/templates/polling_results/polling_unit_result.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Polling Unit Result</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .form-group { margin-bottom: 15px; }
        select { padding: 8px; width: 300px; }
        button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Individual Polling Unit Results</h1>
    
    <form method="get">
        <div class="form-group">
            <label for="polling_unit">Select Polling Unit:</label>
            <select name="polling_unit" id="polling_unit">
                <option value="">-- Select a Polling Unit --</option>
                {% for unit in polling_units %}
                    <option value="{{ unit.polling_unit_id }}" {% if request.GET.polling_unit == unit.polling_unit_id|stringformat:"s" %}selected{% endif %}>
                        {{ unit.polling_unit_name }}
                    </option>
                {% endfor %}
            </select>
        </div>
        <button type="submit">View Results</button>
    </form>
    
    {% if results %}
        <h2>Results:</h2>
        <table>
            <thead>
                <tr>
                    <th>Party</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                {% for result in results %}
                    <tr>
                        <td>{{ result.party.party_name }}</td>
                        <td>{{ result.party_score }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% elif request.GET.polling_unit %}
        <p>No results found for this polling unit.</p>
    {% endif %}
</body>
</html>
"""

# polling_results/templates/polling_results/lga_result.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>LGA Result</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .form-group { margin-bottom: 15px; }
        select { padding: 8px; width: 300px; }
        button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Summed Polling Unit Results by LGA</h1>
    
    <form method="get">
        <div class="form-group">
            <label for="lga">Select Local Government Area:</label>
            <select name="lga" id="lga">
                <option value="">-- Select an LGA --</option>
                {% for lga in lgas %}
                    <option value="{{ lga.lga_id }}" {% if request.GET.lga == lga.lga_id|stringformat:"s" %}selected{% endif %}>
                        {{ lga.lga_name }}
                    </option>
                {% endfor %}
            </select>
        </div>
        <button type="submit">View Results</button>
    </form>
    
    {% if summed_results %}
        <h2>Results for {{ selected_lga.lga_name }} LGA:</h2>
        <table>
            <thead>
                <tr>
                    <th>Party</th>
                    <th>Total Score</th>
                </tr>
            </thead>
            <tbody>
                {% for result in summed_results %}
                    <tr>
                        <td>{{ result.party__party_name }}</td>
                        <td>{{ result.total_score }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% elif request.GET.lga %}
        <p>No results found for this LGA.</p>
    {% endif %}
</body>
</html>
"""

# polling_results/templates/polling_results/new_polling_unit.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>New Polling Unit Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, select { padding: 8px; width: 300px; }
        button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .party-scores { display: flex; flex-wrap: wrap; }
        .party-score { width: 200px; margin: 10px; }
    </style>
</head>
<body>
    <h1>Add New Polling Unit Results</h1>
    
    <form method="post">
        {% csrf_token %}
        
        <div class="form-group">
            <label for="id_polling_unit_name">Polling Unit Name:</label>
            {{ form.polling_unit_name }}
        </div>
        
        <div class="form-group">
            <label for="id_ward">Ward:</label>
            {{ form.ward }}
        </div>
        
        <h2>Party Scores:</h2>
        <div class="party-scores">
            {% for party in parties %}
                <div class="party-score">
                    <label for="id_party_{{ party.party_id }}">{{ party.party_name }}:</label>
                    {{ form.field_party_|add:party.party_id|stringformat:"s" }}
                </div>
            {% endfor %}
        </div>
        
        <button type="submit">Save Results</button>
    </form>
</body>
</html>
"""

# election_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('polling_results.urls')),
]
Last