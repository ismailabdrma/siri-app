from django.core.management.base import BaseCommand
from siri_app.models import CompanyInput
from siri_app.views import calculate_cost_factor, calculate_kpi_factor, calculate_proximity_factor, calculate_impact_value

class Command(BaseCommand):
    help = 'Calculates SIRI metrics for a given company input'

    def handle(self, *args, **kwargs):
        input_values = {
            "vertical_integration_score": 1,
            "horizontal_integration_score": 1,
            "integrated_product_lifecycle_score": 2,
            "shop_floor_automation_score": 1,
            "enterprise_automation_score": 1,
            "facility_automation_score": 0,
            "shop_floor_connectivity_score": 0,
            "enterprise_connectivity_score": 2,
            "facility_connectivity_score": 0,
            "shop_floor_intelligence_score": 1,
            "enterprise_intelligence_score": 2,
            "facility_intelligence_score": 0,
            "workforce_learning_development_score": 2,
            "leadership_competency_score": 1,
            "inter_intra_company_collaboration_score": 2,
            "strategy_governance_score": 1,
            "aftermarket_services_warranty": 1,
            "depreciation": 3.0,
            "labour": 24,
            "maintenance_repair": 1,
            "raw_materials_consumables": 38,
            "rental_operating_lease": 0,
            "research_development": 5,
            "selling_general_administrative_expense": 17,
            "transportation_distribution": 3,
            "utilities": 5,
            "planning_horizon": "Strategic",
            "industry_benchmark": "Electronics",
            "kpi_categories": ["Workforce Efficiency", "Inventory Efficiency", "Process Quality", "Planning & Scheduling Effectiveness", "Workforce Flexibility"]
        }

        class MockCompanyInput:
            def __init__(self, **entries):
                self.__dict__.update(entries)

        company_input = MockCompanyInput(**input_values)

        # Calculate Cost Factor
        cost_factor, total_cost_factor, cost_factor_normalized = calculate_cost_factor(company_input)
        self.stdout.write(self.style.SUCCESS(f'Cost Factor: {cost_factor}'))
        self.stdout.write(self.style.SUCCESS(f'Total Cost Factor: {total_cost_factor}'))
        self.stdout.write(self.style.SUCCESS(f'Cost Factor Normalized: {cost_factor_normalized}'))

        # Calculate KPI Factor
        kpi_factor = calculate_kpi_factor(company_input)
        self.stdout.write(self.style.SUCCESS(f'KPI Factor: {kpi_factor}'))

        # Calculate Proximity Factor
        proximity_factor = calculate_proximity_factor(company_input)
        self.stdout.write(self.style.SUCCESS(f'Proximity Factor: {proximity_factor}'))

        # Calculate Impact Value
        impact_value = calculate_impact_value(cost_factor, kpi_factor, proximity_factor, company_input.planning_horizon)
        self.stdout.write(self.style.SUCCESS(f'Impact Value: {impact_value}'))

        # Determine Prioritised Dimensions
        prioritised_dimensions = sorted(impact_value.items(), key=lambda x: x[1], reverse=True)[:3]
        self.stdout.write(self.style.SUCCESS(f'Prioritised Dimensions: {prioritised_dimensions}'))

