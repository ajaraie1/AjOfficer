// API Types matching backend schemas

// Goal types
export interface Resource {
    id: string;
    goal_id: string;
    resource_type: 'time' | 'effort' | 'money' | 'tool' | 'other';
    name: string;
    description?: string;
    quantity?: number;
    unit?: string;
    created_at: string;
}

export interface Goal {
    id: string;
    user_id: string;
    title: string;
    description?: string;
    purpose: string;
    start_date?: string;
    target_date?: string;
    status: 'draft' | 'active' | 'in_progress' | 'completed' | 'paused' | 'cancelled';
    created_at: string;
    updated_at?: string;
    resources: Resource[];
}

// Process types
export interface ProcessStep {
    id: string;
    process_id: string;
    name: string;
    description?: string;
    action_verb?: string;
    sequence_order: number;
    frequency: 'once' | 'daily' | 'weekly' | 'custom';
    estimated_duration_minutes?: number;
    quality_criteria?: string;
    expected_output?: string;
    is_active: boolean;
    created_at: string;
    updated_at?: string;
}

export interface Process {
    id: string;
    goal_id: string;
    name: string;
    description?: string;
    purpose?: string;
    sequence_order: number;
    status: 'draft' | 'active' | 'completed' | 'paused';
    created_at: string;
    updated_at?: string;
    steps: ProcessStep[];
}

// Daily Operations types
export interface Deviation {
    id: string;
    daily_log_id: string;
    deviation_type: 'time' | 'quality' | 'process' | 'skip' | 'external';
    description: string;
    impact_level?: number;
    root_cause?: string;
    created_at: string;
}

export interface DailyLog {
    id: string;
    step_id: string;
    user_id: string;
    execution_date: string;
    planned_start?: string;
    actual_start?: string;
    actual_end?: string;
    status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'blocked';
    actual_execution?: string;
    output_produced?: string;
    quality_score?: number;
    quality_notes?: string;
    created_at: string;
    updated_at?: string;
    deviations: Deviation[];
}

// Measurement types
export interface Measurement {
    id: string;
    user_id: string;
    measurement_type: 'daily' | 'weekly' | 'process' | 'goal';
    measurement_date: string;
    reference_id?: string;
    execution_accuracy?: number;
    time_deviation?: number;
    quality_compliance?: number;
    process_efficiency?: number;
    raw_data?: Record<string, any>;
    analysis_summary?: string;
    issues_detected?: Array<Record<string, any>>;
    created_at: string;
}

export interface DailyMetrics {
    date: string;
    total_steps: number;
    completed_steps: number;
    completion_rate: number;
    average_quality: number;
    total_deviations: number;
    time_deviation_avg: number;
}

// Control types
export interface Improvement {
    id: string;
    user_id: string;
    target_type: string;
    target_id: string;
    improvement_type: 'simplify' | 'remove' | 'reorder' | 'merge' | 'split' | 'replace' | 'automate';
    title: string;
    description: string;
    rationale?: string;
    status: 'proposed' | 'approved' | 'implemented' | 'rejected';
    expected_time_savings?: number;
    expected_quality_improvement?: number;
    expected_effort_reduction?: number;
    trigger_data?: Record<string, any>;
    implemented_at?: string;
    implementation_notes?: string;
    created_at: string;
    updated_at?: string;
}

// Auth types
export interface User {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    created_at: string;
}

export interface AuthToken {
    access_token: string;
    token_type: string;
}
