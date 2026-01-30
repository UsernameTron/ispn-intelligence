#!/usr/bin/env python3
"""
Genesys QA Analytics - Core Processing Engine
Transforms evaluation_questions CSV exports into actionable coaching intelligence.

Usage:
    from qa_analyzer import GenesysQAAnalyzer
    analyzer = GenesysQAAnalyzer(csv_path)
    results = analyzer.analyze()
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


@dataclass
class AgentPerformance:
    """Agent-level performance summary"""
    name: str
    agent_id: str
    eval_count: int
    total_score: float
    total_max: float
    avg_percentage: float
    std_dev: Optional[float]
    tier: str
    evaluations: List[str] = field(default_factory=list)
    failure_patterns: Dict[str, float] = field(default_factory=dict)


@dataclass
class QuestionAnalysis:
    """Question-level failure analysis"""
    question_id: str
    question_text: str
    group_name: str
    max_points: float
    failure_rate: float
    points_lost: float
    impact_score: float
    help_text: Optional[str]
    fail_count: int
    total_count: int


@dataclass
class EvaluatorCalibration:
    """Evaluator consistency metrics"""
    name: str
    evaluator_id: str
    eval_count: int
    avg_score: float
    std_dev: Optional[float]
    status: str
    deviation_from_norm: float


@dataclass 
class CategoryGap:
    """Category-level gap analysis"""
    name: str
    total_score: float
    total_max: float
    success_rate: float
    gap_percentage: float
    points_at_risk: float


class GenesysQAAnalyzer:
    """
    Main analyzer class for Genesys QA evaluation exports.
    
    Handles:
    - Multi-form normalization (Full Call Review, Auto-Evaluation, Focus Review)
    - Agent performance tiering
    - Question-level failure analysis
    - Evaluator calibration checking
    - Coaching plan generation
    """
    
    # Performance tier thresholds (configurable)
    TIER_THRESHOLDS = {
        'exemplary': 95.0,
        'standard': 80.0,
        'development': 65.0
        # Below development = critical
    }
    
    # Calibration thresholds
    CALIBRATION_THRESHOLDS = {
        'max_std_dev': 15.0,
        'max_mean_deviation': 10.0,
        'min_sample_size': 5
    }
    
    # Expected columns in Genesys export
    REQUIRED_COLUMNS = [
        'EvaluationId', 'EvaluationFormName', 'AgentName', 'AgentId',
        'EvaluatorName', 'EvaluatorId', 'QuestionGroupName', 'QuestionText',
        'QuestionHelpText', 'Score', 'MaxPoints', 'ConversationDate'
    ]
    
    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV path"""
        self.csv_path = csv_path
        self.df = None
        self.validation_errors = []
        
        # Results storage
        self.agents: Dict[str, AgentPerformance] = {}
        self.questions: Dict[str, QuestionAnalysis] = {}
        self.evaluators: Dict[str, EvaluatorCalibration] = {}
        self.categories: Dict[str, CategoryGap] = {}
        
        # Metadata
        self.date_range = (None, None)
        self.eval_count = 0
        self.form_distribution = {}
        self.team_avg = 0.0
        self.team_std = 0.0
        
    def load_and_validate(self) -> bool:
        """Load CSV and validate structure"""
        try:
            self.df = pd.read_csv(self.csv_path)
        except Exception as e:
            self.validation_errors.append(f"Failed to read CSV: {str(e)}")
            return False
        
        # Check required columns
        missing = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing:
            self.validation_errors.append(f"Missing required columns: {missing}")
            return False
        
        # Check for empty dataframe
        if len(self.df) == 0:
            self.validation_errors.append("CSV contains no data rows")
            return False
        
        # Validate Score <= MaxPoints
        invalid_scores = self.df[self.df['Score'] > self.df['MaxPoints']]
        if len(invalid_scores) > 0:
            self.validation_errors.append(
                f"Found {len(invalid_scores)} rows where Score > MaxPoints"
            )
        
        return len(self.validation_errors) == 0
    
    def analyze(self) -> Dict:
        """Run complete analysis pipeline"""
        if not self.load_and_validate():
            return {
                'success': False,
                'errors': self.validation_errors
            }
        
        # Extract metadata
        self._extract_metadata()
        
        # Run analyses
        self._analyze_agents()
        self._analyze_questions()
        self._analyze_evaluators()
        self._analyze_categories()
        
        return self._compile_results()
    
    def _extract_metadata(self):
        """Extract dataset metadata"""
        self.eval_count = self.df['EvaluationId'].nunique()
        
        # Date range
        dates = pd.to_datetime(self.df['ConversationDate'], errors='coerce')
        self.date_range = (
            dates.min().strftime('%Y-%m-%d') if pd.notna(dates.min()) else 'Unknown',
            dates.max().strftime('%Y-%m-%d') if pd.notna(dates.max()) else 'Unknown'
        )
        
        # Form distribution
        self.form_distribution = self.df.groupby('EvaluationFormName')['EvaluationId'].nunique().to_dict()
        
    def _analyze_agents(self):
        """Calculate agent performance metrics and assign tiers"""
        # Group by agent and evaluation to get per-evaluation totals
        eval_scores = self.df.groupby(['AgentName', 'AgentId', 'EvaluationId']).agg({
            'Score': 'sum',
            'MaxPoints': 'sum'
        }).reset_index()
        
        eval_scores['Percentage'] = (eval_scores['Score'] / eval_scores['MaxPoints']) * 100
        
        # Aggregate to agent level
        agent_stats = eval_scores.groupby(['AgentName', 'AgentId']).agg({
            'Percentage': ['mean', 'std', 'count'],
            'Score': 'sum',
            'MaxPoints': 'sum',
            'EvaluationId': list
        }).reset_index()
        
        agent_stats.columns = ['AgentName', 'AgentId', 'AvgPct', 'StdDev', 'EvalCount', 
                               'TotalScore', 'TotalMax', 'Evaluations']
        
        # Calculate team average for calibration baseline
        self.team_avg = agent_stats['AvgPct'].mean()
        self.team_std = agent_stats['AvgPct'].std()
        
        # Assign tiers and create AgentPerformance objects
        for _, row in agent_stats.iterrows():
            tier = self._assign_tier(row['AvgPct'])
            
            # Get failure patterns for this agent
            agent_failures = self._get_agent_failures(row['AgentName'])
            
            self.agents[row['AgentName']] = AgentPerformance(
                name=row['AgentName'],
                agent_id=row['AgentId'],
                eval_count=int(row['EvalCount']),
                total_score=row['TotalScore'],
                total_max=row['TotalMax'],
                avg_percentage=round(row['AvgPct'], 2),
                std_dev=round(row['StdDev'], 2) if pd.notna(row['StdDev']) else None,
                tier=tier,
                evaluations=row['Evaluations'],
                failure_patterns=agent_failures
            )
    
    def _assign_tier(self, avg_pct: float) -> str:
        """Assign performance tier based on average percentage"""
        if avg_pct >= self.TIER_THRESHOLDS['exemplary']:
            return 'Exemplary'
        elif avg_pct >= self.TIER_THRESHOLDS['standard']:
            return 'Standard'
        elif avg_pct >= self.TIER_THRESHOLDS['development']:
            return 'Development'
        else:
            return 'Critical'
    
    def _get_agent_failures(self, agent_name: str) -> Dict[str, float]:
        """Get question failure rates for specific agent"""
        agent_df = self.df[self.df['AgentName'] == agent_name]
        
        failures = {}
        for question in agent_df['QuestionText'].unique():
            q_df = agent_df[agent_df['QuestionText'] == question]
            if len(q_df) > 0 and q_df['MaxPoints'].iloc[0] > 0:
                failure_rate = (q_df['Score'] == 0).sum() / len(q_df) * 100
                if failure_rate > 0:
                    failures[question] = round(failure_rate, 1)
        
        return dict(sorted(failures.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_questions(self):
        """Analyze question-level failure patterns"""
        question_stats = self.df.groupby(
            ['QuestionGroupName', 'QuestionText', 'QuestionId']
        ).agg({
            'Score': ['sum', lambda x: (x == 0).sum(), 'count'],
            'MaxPoints': ['sum', 'first'],
            'QuestionHelpText': 'first'
        }).reset_index()
        
        question_stats.columns = [
            'GroupName', 'QuestionText', 'QuestionId',
            'TotalScore', 'FailCount', 'TotalCount', 'TotalMax', 'MaxPoints', 'HelpText'
        ]
        
        question_stats['FailureRate'] = (question_stats['FailCount'] / question_stats['TotalCount']) * 100
        question_stats['PointsLost'] = question_stats['TotalMax'] - question_stats['TotalScore']
        question_stats['ImpactScore'] = question_stats['FailureRate'] * question_stats['MaxPoints']
        
        for _, row in question_stats.iterrows():
            if pd.isna(row['MaxPoints']) or row['MaxPoints'] == 0:
                continue  # Skip non-scoring questions
                
            self.questions[row['QuestionText']] = QuestionAnalysis(
                question_id=row['QuestionId'],
                question_text=row['QuestionText'],
                group_name=row['GroupName'],
                max_points=row['MaxPoints'],
                failure_rate=round(row['FailureRate'], 1),
                points_lost=row['PointsLost'],
                impact_score=round(row['ImpactScore'], 1),
                help_text=row['HelpText'] if pd.notna(row['HelpText']) else None,
                fail_count=int(row['FailCount']),
                total_count=int(row['TotalCount'])
            )
    
    def _analyze_evaluators(self):
        """Analyze evaluator calibration"""
        # Get per-evaluation scores by evaluator
        eval_scores = self.df.groupby(['EvaluatorName', 'EvaluatorId', 'EvaluationId']).agg({
            'Score': 'sum',
            'MaxPoints': 'sum'
        }).reset_index()
        
        eval_scores['Percentage'] = (eval_scores['Score'] / eval_scores['MaxPoints']) * 100
        
        # Aggregate to evaluator level
        evaluator_stats = eval_scores.groupby(['EvaluatorName', 'EvaluatorId']).agg({
            'Percentage': ['mean', 'std', 'count']
        }).reset_index()
        
        evaluator_stats.columns = ['EvaluatorName', 'EvaluatorId', 'AvgScore', 'StdDev', 'EvalCount']
        
        # Calculate team baseline
        team_mean = evaluator_stats['AvgScore'].mean()
        
        for _, row in evaluator_stats.iterrows():
            deviation = row['AvgScore'] - team_mean
            
            # Determine status
            status = self._determine_calibration_status(
                row['StdDev'], deviation, row['EvalCount']
            )
            
            self.evaluators[row['EvaluatorName']] = EvaluatorCalibration(
                name=row['EvaluatorName'],
                evaluator_id=row['EvaluatorId'],
                eval_count=int(row['EvalCount']),
                avg_score=round(row['AvgScore'], 1),
                std_dev=round(row['StdDev'], 1) if pd.notna(row['StdDev']) else None,
                status=status,
                deviation_from_norm=round(deviation, 1)
            )
    
    def _determine_calibration_status(self, std_dev: float, deviation: float, count: int) -> str:
        """Determine evaluator calibration status"""
        issues = []
        
        if count < self.CALIBRATION_THRESHOLDS['min_sample_size']:
            issues.append('Insufficient Data')
        
        if pd.notna(std_dev) and std_dev > self.CALIBRATION_THRESHOLDS['max_std_dev']:
            issues.append('High Variance')
        
        if abs(deviation) > self.CALIBRATION_THRESHOLDS['max_mean_deviation']:
            if deviation > 0:
                issues.append('Lenient')
            else:
                issues.append('Harsh')
        
        if not issues:
            return 'Calibrated'
        else:
            return ' | '.join(issues)
    
    def _analyze_categories(self):
        """Analyze category-level gaps"""
        cat_stats = self.df.groupby('QuestionGroupName').agg({
            'Score': 'sum',
            'MaxPoints': 'sum'
        }).reset_index()
        
        cat_stats['SuccessRate'] = (cat_stats['Score'] / cat_stats['MaxPoints']) * 100
        cat_stats['GapPct'] = 100 - cat_stats['SuccessRate']
        cat_stats['PointsAtRisk'] = cat_stats['MaxPoints'] - cat_stats['Score']
        
        for _, row in cat_stats.iterrows():
            if pd.isna(row['MaxPoints']) or row['MaxPoints'] == 0:
                continue
                
            self.categories[row['QuestionGroupName']] = CategoryGap(
                name=row['QuestionGroupName'],
                total_score=row['Score'],
                total_max=row['MaxPoints'],
                success_rate=round(row['SuccessRate'], 1),
                gap_percentage=round(row['GapPct'], 1),
                points_at_risk=row['PointsAtRisk']
            )
    
    def _compile_results(self) -> Dict:
        """Compile all analysis results"""
        # Sort agents by tier priority (Critical first) then by score
        tier_order = {'Critical': 0, 'Development': 1, 'Standard': 2, 'Exemplary': 3}
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda x: (tier_order.get(x.tier, 4), x.avg_percentage)
        )
        
        # Sort questions by impact score (highest first)
        sorted_questions = sorted(
            self.questions.values(),
            key=lambda x: x.impact_score,
            reverse=True
        )
        
        # Sort categories by gap (highest first)
        sorted_categories = sorted(
            self.categories.values(),
            key=lambda x: x.gap_percentage,
            reverse=True
        )
        
        # Tier distribution
        tier_counts = {}
        for agent in self.agents.values():
            tier_counts[agent.tier] = tier_counts.get(agent.tier, 0) + 1
        
        return {
            'success': True,
            'metadata': {
                'date_range': self.date_range,
                'evaluation_count': self.eval_count,
                'agent_count': len(self.agents),
                'evaluator_count': len(self.evaluators),
                'form_distribution': self.form_distribution,
                'team_average': round(self.team_avg, 1),
                'team_std': round(self.team_std, 1) if pd.notna(self.team_std) else None
            },
            'tier_distribution': tier_counts,
            'agents': [self._agent_to_dict(a) for a in sorted_agents],
            'questions': [self._question_to_dict(q) for q in sorted_questions],
            'categories': [self._category_to_dict(c) for c in sorted_categories],
            'evaluators': [self._evaluator_to_dict(e) for e in self.evaluators.values()],
            'coaching_needed': [
                self._agent_to_dict(a) for a in sorted_agents 
                if a.tier in ['Critical', 'Development']
            ],
            'calibration_issues': [
                self._evaluator_to_dict(e) for e in self.evaluators.values()
                if e.status != 'Calibrated'
            ]
        }
    
    def _agent_to_dict(self, agent: AgentPerformance) -> Dict:
        return {
            'name': agent.name,
            'agent_id': agent.agent_id,
            'eval_count': agent.eval_count,
            'avg_percentage': agent.avg_percentage,
            'std_dev': agent.std_dev,
            'tier': agent.tier,
            'failure_patterns': agent.failure_patterns
        }
    
    def _question_to_dict(self, question: QuestionAnalysis) -> Dict:
        return {
            'question_text': question.question_text,
            'group_name': question.group_name,
            'max_points': question.max_points,
            'failure_rate': question.failure_rate,
            'points_lost': question.points_lost,
            'impact_score': question.impact_score,
            'help_text': question.help_text,
            'fail_count': question.fail_count,
            'total_count': question.total_count
        }
    
    def _category_to_dict(self, category: CategoryGap) -> Dict:
        return {
            'name': category.name,
            'success_rate': category.success_rate,
            'gap_percentage': category.gap_percentage,
            'points_at_risk': category.points_at_risk
        }
    
    def _evaluator_to_dict(self, evaluator: EvaluatorCalibration) -> Dict:
        return {
            'name': evaluator.name,
            'eval_count': evaluator.eval_count,
            'avg_score': evaluator.avg_score,
            'std_dev': evaluator.std_dev,
            'status': evaluator.status,
            'deviation_from_norm': evaluator.deviation_from_norm
        }
    
    def generate_coaching_plan(self, agent_name: str) -> Optional[str]:
        """Generate detailed coaching plan for specific agent"""
        if agent_name not in self.agents:
            return None
        
        agent = self.agents[agent_name]
        
        if agent.tier not in ['Critical', 'Development']:
            return f"Agent {agent_name} is in {agent.tier} tier - no coaching plan required."
        
        # Get top failure patterns with coaching criteria
        coaching_items = []
        for question_text, failure_rate in list(agent.failure_patterns.items())[:5]:
            if question_text in self.questions:
                q = self.questions[question_text]
                coaching_items.append({
                    'question': question_text,
                    'group': q.group_name,
                    'failure_rate': failure_rate,
                    'points_at_risk': q.max_points,
                    'help_text': q.help_text,
                    'team_avg_failure': q.failure_rate
                })
        
        # Generate plan
        plan = f"""
═══════════════════════════════════════════════════════════════════════════════
AGENT COACHING PLAN
═══════════════════════════════════════════════════════════════════════════════

Agent: {agent.name}
Performance Tier: {agent.tier}
Current Score: {agent.avg_percentage}% | Target: ≥80% | Gap: {max(0, 80 - agent.avg_percentage):.1f}%
Evaluations Analyzed: {agent.eval_count}
Score Consistency (σ): {agent.std_dev if agent.std_dev else 'N/A'}

───────────────────────────────────────────────────────────────────────────────
PRIORITY COACHING AREAS (Ranked by Impact)
───────────────────────────────────────────────────────────────────────────────
"""
        
        for i, item in enumerate(coaching_items, 1):
            plan += f"""
{i}. {item['question'][:60]}{'...' if len(item['question']) > 60 else ''}
   Category: {item['group']}
   Agent Failure Rate: {item['failure_rate']}% (Team avg: {item['team_avg_failure']}%)
   Points at Risk: {item['points_at_risk']} per evaluation
   
   BEHAVIORAL CRITERIA:
"""
            if item['help_text']:
                # Wrap help text
                help_lines = item['help_text'].split('\n')
                for line in help_lines:
                    if line.strip():
                        plan += f"   {line.strip()}\n"
            else:
                plan += "   [No specific criteria documented - review with QA team]\n"
            
            plan += """
   COACHING ACTIONS:
   • Demonstrate correct behavior in role-play scenario
   • Review 2-3 exemplary call recordings showing this skill
   • Practice with feedback in next 5 live calls
"""
        
        plan += f"""
───────────────────────────────────────────────────────────────────────────────
SUCCESS METRICS
───────────────────────────────────────────────────────────────────────────────
• Target: Move to Standard tier (≥80%) within 30 days
• Checkpoint: Re-evaluate minimum 3 calls in 2 weeks
• KPI: Zero failures on Priority 1-2 items in next evaluation cycle
• Progress Review: Weekly 1:1 with supervisor to review call samples

───────────────────────────────────────────────────────────────────────────────
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
═══════════════════════════════════════════════════════════════════════════════
"""
        return plan


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python qa_analyzer.py <csv_path>")
        sys.exit(1)
    
    analyzer = GenesysQAAnalyzer(sys.argv[1])
    results = analyzer.analyze()
    
    if results['success']:
        print(json.dumps(results, indent=2, default=str))
    else:
        print("Analysis failed:")
        for error in results['errors']:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
