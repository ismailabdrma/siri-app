from django import forms
from .models import Company, CompanyInput
from multiselectfield import MultiSelectFormField

KPI_CHOICES = [
    ('Asset & Equipment Efficiency', 'Asset & Equipment Efficiency'),
    ('Workforce Efficiency', 'Workforce Efficiency'),
    ('Utility Efficiency', 'Utility Efficiency'),
    ('Inventory Efficiency', 'Inventory Efficiency'),
    ('Materials Efficiency', 'Materials Efficiency'),
    ('Process Quality', 'Process Quality'),
    ('Product Quality', 'Product Quality'),
    ('Safety', 'Safety'),
    ('Security', 'Security'),
    ('Planning & Scheduling Effectiveness', 'Planning & Scheduling Effectiveness'),
    ('Production Flexibility', 'Production Flexibility'),
    ('Workforce Flexibility', 'Workforce Flexibility'),
    ('Time to Market', 'Time to Market'),
    ('Time to Delivery', 'Time to Delivery')
]

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'industry']

class CompanyInputForm(forms.ModelForm):
    kpi_categories = MultiSelectFormField(choices=KPI_CHOICES,flat_choices=KPI_CHOICES)

    class Meta:
        model = CompanyInput
        fields = [
            'vertical_integration_score', 'horizontal_integration_score', 'integrated_product_lifecycle_score',
            'shop_floor_automation_score', 'enterprise_automation_score', 'facility_automation_score',
            'shop_floor_connectivity_score', 'enterprise_connectivity_score', 'facility_connectivity_score',
            'shop_floor_intelligence_score', 'enterprise_intelligence_score', 'facility_intelligence_score',
            'workforce_learning_development_score', 'leadership_competency_score', 'inter_intra_company_collaboration_score',
            'strategy_governance_score', 'aftermarket_services_warranty', 'depreciation', 'labour', 'maintenance_repair',
            'raw_materials_consumables', 'rental_operating_lease', 'research_development', 'selling_general_administrative_expense',
            'transportation_distribution', 'utilities', 'kpi_categories', 'industry_benchmark', 'planning_horizon'
        ]
        widgets = {
            'kpi_categories': forms.CheckboxSelectMultiple,
            'planning_horizon': forms.Select(choices=[('Strategic', 'Strategic'), ('Tactical', 'Tactical'), ('Operational', 'Operational')]),
            'industry_benchmark': forms.Select(choices=[
                ('Aerospace', 'Aerospace'), ('Automotive', 'Automotive'), ('Electronics', 'Electronics'), # Add all benchmarks
            ]),
        }
