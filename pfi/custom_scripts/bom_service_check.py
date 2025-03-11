# pfi/custom_scripts/bom_service_check.py
from erpnext.manufacturing.doctype.bom.bom import BOM as OriginalBOM
class CustomBOM(OriginalBOM):
    def validate_materials(self):
        if self.is_service_bom:
            self.items = []  # Clear items table
            self.flags.ignore_mandatory = True  # Bypass framework-level checks
            return
            
        super().validate_materials()

    def validate_rm(self):
        """Override original item existence check"""
        if not self.is_service_bom:
            super().validate_rm()
            
    def calculate_rm_cost(self, save=False):
        """Override to exclude raw material cost calculation for service BOMs"""
        if self.is_service_bom:
            # Clear raw material costs for service BOMs
            self.raw_material_cost = 0
            self.base_raw_material_cost = 0
            return
            
        # Run original calculation for non-service BOMs
        super().calculate_rm_cost(save)
