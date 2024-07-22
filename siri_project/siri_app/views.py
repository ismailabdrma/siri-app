from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Company, CompanyInput, SIRICalculation
from .forms import CompanyForm, CompanyInputForm

def home(request):
    return render(request, 'siri_app/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')
@login_required
def companies(request):
    user_companies = Company.objects.filter(user=request.user)
    companies_with_results = []
    companies_without_results = []

    for company in user_companies:
        company_inputs = CompanyInput.objects.filter(company=company).order_by('-id')
        if company_inputs.exists():
            latest_company_input = company_inputs.first()
            siri_calculation = SIRICalculation.objects.filter(company_input=latest_company_input).order_by('-created_at').first()
            if siri_calculation:
                companies_with_results.append({
                    'name': company.name,
                    'id': company.id,
                    'latest_result_timestamp': siri_calculation.created_at,
                })
            else:
                companies_without_results.append({
                    'name': company.name,
                    'id': company.id,
                })
        else:
            companies_without_results.append({
                'name': company.name,
                'id': company.id,
            })

    return render(request, 'siri_app/companies.html', {
        'companies_with_results': companies_with_results,
        'companies_without_results': companies_without_results
    })
@login_required
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            return redirect('companies')
    else:
        form = CompanyForm()
    return render(request, 'siri_app/add_company.html', {'form': form})

@login_required
def input_siri(request, company_id):
    company = get_object_or_404(Company, id=company_id, user=request.user)
    if request.method == 'POST':
        form = CompanyInputForm(request.POST)
        if form.is_valid():
            try:
                company_input = form.save(commit=False)
                company_input.company = company
                company_input.save()
                perform_calculations(company_input)
                return redirect('result', company_id=company.id)
            except Exception as e:
                form.add_error(None, "There was an error processing your input. Please check your values and try again.")
        else:
            print("Form is not valid. Errors:", form.errors)
    else:
        form = CompanyInputForm()
    return render(request, 'siri_app/siri_input.html', {'form': form, 'company': company})
from django.shortcuts import render, get_object_or_404
from siri_app.models import Company, CompanyInput, SIRICalculation

def result(request, company_id):
    company = get_object_or_404(Company, id=company_id, user=request.user)
    company_inputs = CompanyInput.objects.filter(company=company).order_by('-id')
    
    if not company_inputs.exists():
        return render(request, 'siri_app/no_results.html', {'company': company})
    
    latest_company_input = company_inputs.first()
    siri_calculation = get_object_or_404(SIRICalculation, company_input=latest_company_input)

    # Define the categories
    process_dimensions = [
        'Vertical Integration', 'Horizontal Integration', 'Integrated Product Lifecycle', 
        'Shop Floor Automation', 'Enterprise Automation', 'Facility Automation'
    ]
    technology_dimensions = [
        'Shop Floor Connectivity', 'Enterprise Connectivity', 'Facility Connectivity', 
        'Shop Floor Intelligence', 'Enterprise Intelligence', 'Facility Intelligence'
    ]
    organisation_dimensions = [
        'Workforce Learning & Development', 'Leadership Competency', 
        'Inter- & Intra- Company Collaboration', 'Strategy & Governance'
    ]

    # Determine the highest Impact Value in each category
    impact_values = siri_calculation.impact_value
    highest_process = max((dim for dim in process_dimensions), key=lambda dim: impact_values.get(dim, 0))
    highest_technology = max((dim for dim in technology_dimensions), key=lambda dim: impact_values.get(dim, 0))
    highest_organisation = max((dim for dim in organisation_dimensions), key=lambda dim: impact_values.get(dim, 0))

    # Remove the highest Impact Values from the list
    remaining_dimensions = set(impact_values.keys()) - {highest_process, highest_technology, highest_organisation}

    # Identify the highest remaining Impact Value
    highest_remaining = max(remaining_dimensions, key=lambda dim: impact_values.get(dim, 0))

    # Prioritized dimensions
    prioritized_dimensions = [
        (highest_process, impact_values[highest_process]),
        (highest_technology, impact_values[highest_technology]),
        (highest_organisation, impact_values[highest_organisation]),
        (highest_remaining, impact_values[highest_remaining])
    ]

    context = {
        'siri_calculation': siri_calculation,
        'prioritized_dimensions': prioritized_dimensions
    }

    return render(request, 'siri_app/result.html', context)

def perform_calculations(company_input):
    try:
        # Calculate cost factor
        cost_factor, total_cost_factor, cost_factor_normalized = calculate_cost_factor(company_input)
        
        # Calculate KPI factor
        kpi_factor, total_kpi_factor, kpi_factor_normalized = calculate_kpi_factor(company_input)
        
        # Calculate proximity factor
        proximity_factor, total_proximity_factor, proximity_factor_normalized = calculate_proximity_factor(company_input)
        
        # Calculate impact value
        impact_value = calculate_impact_value(cost_factor_normalized, kpi_factor_normalized, proximity_factor_normalized, company_input.planning_horizon)
        
        # Determine prioritized dimensions
        prioritized_dimensions = sorted(impact_value.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Save SIRICalculation
        SIRICalculation.objects.create(
            company_input=company_input,
            cost_factor=cost_factor,
            total_cost_factor=total_cost_factor,
            normalized_cost_factor=cost_factor_normalized,
            kpi_factor=kpi_factor,
            total_kpi_factor=total_kpi_factor,
            normalized_kpi_factor=kpi_factor_normalized,
            proximity_factor=proximity_factor,
            total_proximity_factor=total_proximity_factor,
            normalized_proximity_factor=proximity_factor_normalized,
            impact_value=impact_value,
            prioritized_dimensions=prioritized_dimensions
        )
    except Exception as e:
        print("Error in perform_calculations:", e)
        raise


 
def calculate_cost_factor(company_input):
    DORc_values = {
        'Vertical Integration': [0, 1, 3, 3, 3, 1, 1, 1, 0, 1],
        'Horizontal Integration': [1, 0, 0, 1, 3, 1, 1, 3, 3, 1],
        'Integrated Product Lifecycle': [3, 0, 0, 1, 1, 0, 3, 1, 0, 0],
        'Shop Floor Automation': [0, 0, 3, 1, 1, 1, 0, 0, 0, 1],
        'Enterprise Automation': [3, 0, 0, 1, 1, 1, 3, 3, 1, 1],
        'Facility Automation': [0, 0, 3, 1, 1, 1, 0, 0, 0, 3],
        'Shop Floor Connectivity': [0, 1, 1, 1, 1, 1, 0, 0, 0, 1],
        'Enterprise Connectivity': [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        'Facility Connectivity': [0, 1, 1, 1, 1, 1, 0, 0, 0, 1],
        'Shop Floor Intelligence': [0, 1, 3, 3, 3, 1, 0, 0, 0, 1],
        'Enterprise Intelligence': [3, 0, 0, 1, 3, 1, 3, 3, 3, 1],
        'Facility Intelligence': [0, 1, 3, 3, 1, 1, 0, 0, 0, 3],
        'Workforce Learning & Development': [1, 0, 3, 3, 0, 0, 3, 3, 1, 0],
        'Leadership Competency': [1, 1, 3, 1, 1, 1, 1, 3, 1, 1],
        'Inter- & Intra- Company Collaboration': [1, 0, 3, 1, 1, 0, 3, 3, 3, 0],
        'Strategy & Governance': [1, 1, 3, 1, 1, 1, 3, 3, 1, 1]
    }

    cost_profile = [
        company_input.aftermarket_services_warranty / 100,
        company_input.depreciation / 100,
        company_input.labour / 100,
        company_input.maintenance_repair / 100,
        company_input.raw_materials_consumables / 100,
        company_input.rental_operating_lease / 100,
        company_input.research_development / 100,
        company_input.selling_general_administrative_expense / 100,
        company_input.transportation_distribution / 100,
        company_input.utilities / 100,
    ]

    cost_factor = {}
    total_cost_factor = 0
    for dimension, dorc_values in DORc_values.items():
        total_cost = sum(dorc * cost for dorc, cost in zip(dorc_values, cost_profile))
        cost_factor[dimension] = round(total_cost, 2)
        total_cost_factor += total_cost

    normalized_cost_factor = {dim: round(cf / total_cost_factor, 4) for dim, cf in cost_factor.items()}

    return cost_factor, round(total_cost_factor, 2), normalized_cost_factor
def calculate_kpi_factor(company_input):
    kpi_categories = company_input.kpi_categories
    print("Calculating KPI Factor for categories:", kpi_categories)  # Debug statement
       
    # Define the Degree of Relevance (DOR) table
    DOR_table = {
        
        'Vertical Integration': [3, 3, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 0, 3],
        'Horizontal Integration': [1, 3, 0, 3, 0, 1, 1, 0, 1, 3, 1, 1, 0, 3],
        'Integrated Product Lifecycle': [0, 3, 0, 0, 3, 1, 3, 0, 1, 0, 0, 1, 3, 0],
        'Shop Floor Automation': [3, 3, 1, 3, 1, 3, 3, 3, 0, 0, 3, 1, 0, 3],
        'Enterprise Automation': [1, 3, 0, 3, 1, 3, 1, 0, 0, 3, 0, 1, 3, 3],
        'Facility Automation': [3, 3, 3, 0, 0, 3, 1, 3, 0, 0, 1, 1, 0, 1],
        'Shop Floor Connectivity': [3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 3, 0, 3],
        'Enterprise Connectivity': [1, 1, 0, 1, 1, 1, 1, 0, 3, 3, 0, 1, 3, 3],
        'Facility Connectivity': [3, 1, 3, 0, 0, 1, 1, 1, 3, 0, 1, 3, 0, 1],
        'Shop Floor Intelligence': [3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3, 0, 3],
        'Enterprise Intelligence': [1, 3, 0, 3, 3, 3, 1, 0, 1, 3, 0, 1, 3, 3],
        'Facility Intelligence': [3, 3, 3, 0, 0, 3, 1, 3, 1, 0, 1, 3, 0, 1],
        'Workforce Learning & Development': [1, 3, 1, 1, 1, 3, 3, 1, 3, 1, 1, 3, 1, 1],
        'Leadership Competency': [1, 3, 1, 1, 1, 3, 1, 3, 3, 1, 3, 3, 3, 3],
        'Inter- & Intra- Company Collaboration': [1, 3, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 1, 3],
        'Strategy & Governance': [1, 3, 1, 1, 1, 1, 1, 1, 3, 1, 3, 3, 3, 1]
    }

   # Define the mapping of KPI categories to their indices
    kpi_mapping = {
        'Asset & Equipment Efficiency': 0,
        'Workforce Efficiency': 1,
        'Utility Efficiency': 2,
        'Inventory Efficiency': 3,
        'Materials Efficiency': 4,
        'Process Quality': 5,
        'Product Quality': 6,
        'Safety': 7,
        'Security': 8,
        'Planning & Scheduling Effectiveness': 9,
        'Production Flexibility': 10,
        'Workforce Flexibility': 11,
        'Time to Market': 12,
        'Time to Delivery': 13
    }

    input_vector = [1 if kpi_mapping[kpi] in [kpi_mapping[cat] for cat in kpi_categories] else 0 for kpi in kpi_mapping.keys()]

    # Calculate the KPI factor for each dimension
    kpi_factor = {}
    for dimension, values in DOR_table.items():
        kpi_sum = 0
        for value, input_val in zip(values, input_vector):
            kpi_sum += value * input_val
        kpi_factor[dimension] = kpi_sum

    total_kpi_factor = sum(kpi_factor.values())
    normalized_kpi_factor = {
        dimension: round(value / total_kpi_factor, 4)
        for dimension, value in kpi_factor.items()
    }

    print("Calculated kpi_factor:", kpi_factor)  # Debug statement
    return kpi_factor, total_kpi_factor, normalized_kpi_factor


def calculate_proximity_factor(company_input):
    benchmarks_table = {
        'Aerospace': {
            'Vertical Integration': 3, 'Horizontal Integration': 3, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 2,
            'Enterprise Automation': 3, 'Facility Automation': 4, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 3, 'Leadership Competency': 3, 'Inter- & Intra- Company Collaboration': 3, 'Strategy & Governance': 3
        },
        'Automotive': {
            'Vertical Integration': 3, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 4, 'Shop Floor Automation': 2,
            'Enterprise Automation': 3, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'Electronics': {
              'Vertical Integration': 4, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 3,
            'Enterprise Automation': 3, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 3, 'Shop Floor Intelligence': 5, 'Enterprise Intelligence': 4, 'Facility Intelligence': 4,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4},
        'Energy & Chemicals': {
            'Vertical Integration': 4, 'Horizontal Integration': 3, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 3,
            'Enterprise Automation': 3, 'Facility Automation': 3, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 4, 'Shop Floor Intelligence': 4, 'Enterprise Intelligence': 3, 'Facility Intelligence': 4,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'Food & Beverage': {
            'Vertical Integration': 4, 'Horizontal Integration': 3, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 3,
            'Enterprise Automation': 3, 'Facility Automation': 3, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 4, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 2, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'General Manufacturing': {
            'Vertical Integration': 4, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 4, 'Shop Floor Automation': 3,
            'Enterprise Automation': 3, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'Logistics': {
            'Vertical Integration': 2, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 3,
            'Enterprise Automation': 4, 'Facility Automation': 3, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 4, 'Shop Floor Intelligence': 2, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 3, 'Leadership Competency': 3, 'Inter- & Intra- Company Collaboration': 3, 'Strategy & Governance': 3
        },
        'Machinery & Equipment': {
            'Vertical Integration': 3, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 4, 'Shop Floor Automation': 2,
            'Enterprise Automation': 2, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 2, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 3, 'Leadership Competency': 3, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 3
        },
        'Mardical Technology': {
            'Vertical Integration': 4, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 4,
            'Enterprise Automation': 3, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 2, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'Oil & Gas': {
            'Vertical Integration': 2, 'Horizontal Integration': 3, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 2,
            'Enterprise Automation': 2, 'Facility Automation': 2, 'Shop Floor Connectivity': 2, 'Enterprise Connectivity': 3,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 2, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 2, 'Leadership Competency': 2, 'Inter- & Intra- Company Collaboration': 2, 'Strategy & Governance': 2
        },
        'Pharmaceuticals': {
            'Vertical Integration': 3, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 4, 'Shop Floor Automation': 4,
            'Enterprise Automation': 4, 'Facility Automation': 4, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 4, 'Shop Floor Intelligence': 4, 'Enterprise Intelligence': 3, 'Facility Intelligence': 4,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'Precision Parts': {
            'Vertical Integration': 3, 'Horizontal Integration': 3, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 3,
            'Enterprise Automation': 3, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 2, 'Enterprise Intelligence': 2, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 3, 'Leadership Competency': 3, 'Inter- & Intra- Company Collaboration': 3, 'Strategy & Governance': 3
        },
        'Semiconductors': {
            'Vertical Integration': 4, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 3, 'Shop Floor Automation': 3,
            'Enterprise Automation': 3, 'Facility Automation': 3, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 4, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 4, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        },
        'Textiles (Fabric, Garments, Leather & Footwear)': {
            'Vertical Integration': 3, 'Horizontal Integration': 4, 'Integrated Product Lifecycle': 4, 'Shop Floor Automation': 2,
            'Enterprise Automation': 3, 'Facility Automation': 2, 'Shop Floor Connectivity': 4, 'Enterprise Connectivity': 4,
            'Facility Connectivity': 2, 'Shop Floor Intelligence': 3, 'Enterprise Intelligence': 3, 'Facility Intelligence': 2,
            'Workforce Learning & Development': 3, 'Leadership Competency': 4, 'Inter- & Intra- Company Collaboration': 4, 'Strategy & Governance': 4
        }, }
    
    assessment_matrix_score = {
        'Vertical Integration': company_input.vertical_integration_score,
        'Horizontal Integration': company_input.horizontal_integration_score,
        'Integrated Product Lifecycle': company_input.integrated_product_lifecycle_score,
        'Shop Floor Automation': company_input.shop_floor_automation_score,
        'Enterprise Automation': company_input.enterprise_automation_score,
        'Facility Automation': company_input.facility_automation_score,
        'Shop Floor Connectivity': company_input.shop_floor_connectivity_score,
        'Enterprise Connectivity': company_input.enterprise_connectivity_score,
        'Facility Connectivity': company_input.facility_connectivity_score,
        'Shop Floor Intelligence': company_input.shop_floor_intelligence_score,
        'Enterprise Intelligence': company_input.enterprise_intelligence_score,
        'Facility Intelligence': company_input.facility_intelligence_score,
        'Workforce Learning & Development': company_input.workforce_learning_development_score,
        'Leadership Competency': company_input.leadership_competency_score,
        'Inter- & Intra- Company Collaboration': company_input.inter_intra_company_collaboration_score,
        'Strategy & Governance': company_input.strategy_governance_score,
    }

    industry_benchmark = benchmarks_table[company_input.industry_benchmark]
    proximity_factor = {
        dimension: max(industry_benchmark[dimension] - assessment_matrix_score[dimension], 0)
        for dimension in assessment_matrix_score
    }

    total_proximity_factor = sum(proximity_factor.values())
    normalized_proximity_factor = {
        dimension: round(value / total_proximity_factor, 4)
        for dimension, value in proximity_factor.items()
    }

    return proximity_factor, total_proximity_factor, normalized_proximity_factor




      
def calculate_impact_value(normalized_cost_factor, normalized_kpi_factor, normalized_proximity_factor, planning_horizon):
    selected_weights = {
        'strategic': {'cost': 0.3, 'kpi': 0.4, 'proximity': 0.3},
        'tactical': {'cost': 0.4, 'kpi': 0.3, 'proximity': 0.3},
        'operational': {'cost': 0.3, 'kpi': 0.3, 'proximity': 0.4}
    }

    # Convert planning horizon to lowercase to match keys in selected_weights
    planning_horizon = planning_horizon.lower()

    # Fetch weights based on planning horizon
    weights = selected_weights[planning_horizon]

    impact_value = {}
    for dimension in normalized_cost_factor.keys():
        impact_value[dimension] = (
            weights['kpi'] * normalized_kpi_factor.get(dimension, 0) +
            weights['proximity'] * normalized_proximity_factor.get(dimension, 0) +
            weights['cost'] * normalized_cost_factor.get(dimension, 0)
        )

    return impact_value


from django.shortcuts import render

def about(request):
    return render(request, 'siri_app/about.html')
