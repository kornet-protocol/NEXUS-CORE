// =====================================================================
// NEXUS KORNET ENGINE: CYBERNETIC RESOURCE BALANCER v0.1
// Leontief Input-Output Model with Simplex Optimization on GPU
// =====================================================================

use std::collections::HashMap;

pub struct ResourceBalancer {
    pub technological_matrix: Vec<Vec<f64>>,
    pub needs_vector: Vec<f64>,
    pub resource_names: Vec<String>,
}

impl ResourceBalancer {
    pub fn new(resource_names: Vec<String>) -> Self {
        let n = resource_names.len();
        Self {
            technological_matrix: vec![vec![0.0; n]; n],
            needs_vector: vec![0.0; n],
            resource_names,
        }
    }

    pub fn set_technology_coefficient(&mut self, from: usize, to: usize, coefficient: f64) {
        if from < self.technological_matrix.len() && to < self.technological_matrix[from].len() {
            self.technological_matrix[from][to] = coefficient;
        }
    }

    pub fn set_need(&mut self, resource: usize, amount: f64) {
        if resource < self.needs_vector.len() {
            self.needs_vector[resource] = amount;
        }
    }

    /// Leontief solution: X = (I - A)^(-1) * Y
    /// Simplified for demonstration: X = Y + A * Y
    pub fn calculate_distribution(&self) -> HashMap<String, f64> {
        let n = self.technological_matrix.len();
        let mut distribution: HashMap<String, f64> = HashMap::new();
        
        for i in 0..n {
            let mut x_i = self.needs_vector[i];
            for j in 0..n {
                x_i += self.technological_matrix[i][j] * self.needs_vector[j];
            }
            distribution.insert(self.resource_names[i].clone(), x_i);
        }
        
        distribution
    }

    /// Simplex placeholder: route scarce resources to highest mortality-reduction impact
    pub fn optimize_scarce_resource(&self, scarce_resource: &str, demands: &[(String, f64, f64)]) -> Vec<(String, f64)> {
        // demands: (project_id, requested_amount, mortality_reduction_impact)
        let _ = scarce_resource;
        let total_demand: f64 = demands.iter().map(|(_, req, _)| *req).sum();
        if total_demand == 0.0 {
            return demands.iter().map(|(pid, _, _)| (pid.clone(), 0.0)).collect();
        }
        
        let total_impact: f64 = demands.iter().map(|(_, _, impact)| *impact).sum();
        if total_impact == 0.0 {
            return demands.iter().map(|(pid, req, _)| (pid.clone(), *req)).collect();
        }
        
        demands.iter().map(|(pid, req, impact)| {
            let share = impact / total_impact;
            (pid.clone(), req * share)
        }).collect()
    }
}