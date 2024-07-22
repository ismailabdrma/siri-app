from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

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

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    industry = models.CharField(max_length=255)

class CompanyInput(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    vertical_integration_score = models.IntegerField()
    horizontal_integration_score = models.IntegerField()
    integrated_product_lifecycle_score = models.IntegerField()
    shop_floor_automation_score = models.IntegerField()
    enterprise_automation_score = models.IntegerField()
    facility_automation_score = models.IntegerField()
    shop_floor_connectivity_score = models.IntegerField()
    enterprise_connectivity_score = models.IntegerField()
    facility_connectivity_score = models.IntegerField()
    shop_floor_intelligence_score = models.IntegerField()
    enterprise_intelligence_score = models.IntegerField()
    facility_intelligence_score = models.IntegerField()
    workforce_learning_development_score = models.IntegerField()
    leadership_competency_score = models.IntegerField()
    inter_intra_company_collaboration_score = models.IntegerField()
    strategy_governance_score = models.IntegerField()
    aftermarket_services_warranty = models.FloatField()
    depreciation = models.FloatField()
    labour = models.FloatField()
    maintenance_repair = models.FloatField()
    raw_materials_consumables = models.FloatField()
    rental_operating_lease = models.FloatField()
    research_development = models.FloatField()
    selling_general_administrative_expense = models.FloatField()
    transportation_distribution = models.FloatField()
    utilities = models.FloatField()
    kpi_categories = MultiSelectField(choices=KPI_CHOICES)
    industry_benchmark = models.CharField(max_length=255)
    planning_horizon = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
class SIRICalculation(models.Model):
    company_input = models.OneToOneField(CompanyInput, on_delete=models.CASCADE)
    cost_factor = models.JSONField()
    total_cost_factor = models.FloatField()
    normalized_cost_factor = models.JSONField()
    kpi_factor = models.JSONField()
    total_kpi_factor = models.FloatField()
    normalized_kpi_factor = models.JSONField()
    proximity_factor = models.JSONField()
    total_proximity_factor = models.FloatField()
    normalized_proximity_factor = models.JSONField()
    impact_value = models.JSONField()
    prioritized_dimensions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)