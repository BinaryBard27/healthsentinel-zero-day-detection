"""
Threshold Tuning Utilities for Insider Threat Detection
========================================================

Tools for optimizing detection thresholds based on operational requirements:
- Maximize recall (catch all threats, even with false positives)
- Maximize precision (minimize false positives)
- Balance both (optimize F1 score)

Author: HealthSentinel Team
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from sklearn.metrics import precision_recall_curve, roc_curve, auc, f1_score


class ThresholdTuner:
    """
    Tune detection thresholds for optimal performance.
    
    Healthcare typically prioritizes HIGH RECALL (catch all threats)
    even at cost of some false positives.
    """
    
    def __init__(self):
        self.results = {}
    
    def find_optimal_threshold(self, 
                              y_true: np.ndarray,
                              reconstruction_errors: np.ndarray,
                              target_recall: float = 0.95,
                              target_precision: float = None) -> Dict:
        """
        Find optimal threshold based on operational requirements.
        
        Args:
            y_true: True labels (0=normal, 1=threat)
            reconstruction_errors: Model reconstruction errors
            target_recall: Target recall rate (default: 95%)
            target_precision: Target precision rate (optional)
        
        Returns:
            Dictionary with threshold recommendations
        """
        print(f"🔧 Finding optimal thresholds...")
        print(f"   Samples: {len(y_true):,}")
        print(f"   Positives: {np.sum(y_true):,} ({np.sum(y_true)/len(y_true)*100:.1f}%)")
        
        results = {}
        
        # Sort by reconstruction error
        sorted_indices = np.argsort(reconstruction_errors)
        sorted_errors = reconstruction_errors[sorted_indices]
        sorted_labels = y_true[sorted_indices]
        
        # Compute precision, recall for all possible thresholds
        precision, recall, thresholds = precision_recall_curve(y_true, reconstruction_errors)
        
        # 1. Threshold for target recall
        if target_recall:
            idx = np.argmin(np.abs(recall - target_recall))
            threshold = thresholds[idx] if idx < len(thresholds) else reconstruction_errors.max()
            
            y_pred = (reconstruction_errors >= threshold).astype(int)
            
            results['recall_optimized'] = {
                'threshold': float(threshold),
                'precision': float(precision[idx]),
                'recall': float(recall[idx]),
                'f1': float(2 * precision[idx] * recall[idx] / (precision[idx] + recall[idx] + 1e-10)),
                'false_positive_rate': float(np.sum((y_pred == 1) & (y_true == 0)) / np.sum(y_true == 0)),
                'false_negative_rate': float(np.sum((y_pred == 0) & (y_true == 1)) / np.sum(y_true == 1))
            }
            
            print(f"\n📊 Threshold for {target_recall*100}% Recall:")
            print(f"   Threshold: {results['recall_optimized']['threshold']:.6f}")
            print(f"   Precision: {results['recall_optimized']['precision']:.4f}")
            print(f"   Recall: {results['recall_optimized']['recall']:.4f}")
            print(f"   F1: {results['recall_optimized']['f1']:.4f}")
            print(f"   FPR: {results['recall_optimized']['false_positive_rate']:.4f}")
        
        # 2. Threshold for target precision
        if target_precision:
            idx = np.argmin(np.abs(precision - target_precision))
            threshold = thresholds[idx] if idx < len(thresholds) else reconstruction_errors.max()
            
            y_pred = (reconstruction_errors >= threshold).astype(int)
            
            results['precision_optimized'] = {
                'threshold': float(threshold),
                'precision': float(precision[idx]),
                'recall': float(recall[idx]),
                'f1': float(2 * precision[idx] * recall[idx] / (precision[idx] + recall[idx] + 1e-10))
            }
            
            print(f"\n📊 Threshold for {target_precision*100}% Precision:")
            print(f"   Threshold: {results['precision_optimized']['threshold']:.6f}")
            print(f"   Precision: {results['precision_optimized']['precision']:.4f}")
            print(f"   Recall: {results['precision_optimized']['recall']:.4f}")
            print(f"   F1: {results['precision_optimized']['f1']:.4f}")
        
        # 3. F1-optimal threshold
        f1_scores = 2 * precision * recall / (precision + recall + 1e-10)
        idx = np.argmax(f1_scores)
        threshold = thresholds[idx] if idx < len(thresholds) else reconstruction_errors.max()
        
        y_pred = (reconstruction_errors >= threshold).astype(int)
        
        results['f1_optimized'] = {
            'threshold': float(threshold),
            'precision': float(precision[idx]),
            'recall': float(recall[idx]),
            'f1': float(f1_scores[idx])
        }
        
        print(f"\n📊 Threshold for Best F1:")
        print(f"   Threshold: {results['f1_optimized']['threshold']:.6f}")
        print(f"   Precision: {results['f1_optimized']['precision']:.4f}")
        print(f"   Recall: {results['f1_optimized']['recall']:.4f}")
        print(f"   F1: {results['f1_optimized']['f1']:.4f}")
        
        # 4. Percentile-based thresholds
        for percentile in [90, 95, 99]:
            threshold = np.percentile(reconstruction_errors[y_true == 0], percentile)
            y_pred = (reconstruction_errors >= threshold).astype(int)
            
            prec = np.sum((y_pred == 1) & (y_true == 1)) / (np.sum(y_pred == 1) + 1e-10)
            rec = np.sum((y_pred == 1) & (y_true == 1)) / (np.sum(y_true == 1) + 1e-10)
            
            results[f'p{percentile}'] = {
                'threshold': float(threshold),
                'precision': float(prec),
                'recall': float(rec),
                'f1': float(2 * prec * rec / (prec + rec + 1e-10))
            }
        
        print(f"\n📊 Percentile-based thresholds:")
        for percentile in [90, 95, 99]:
            r = results[f'p{percentile}']
            print(f"   P{percentile}: {r['threshold']:.6f} (Prec={r['precision']:.3f}, Rec={r['recall']:.3f}, F1={r['f1']:.3f})")
        
        self.results = results
        return results
    
    def plot_threshold_analysis(self, y_true: np.ndarray, 
                               reconstruction_errors: np.ndarray,
                               save_path: str = None):
        """
        Create visualization of threshold analysis.
        
        Args:
            y_true: True labels
            reconstruction_errors: Reconstruction errors
            save_path: Path to save plot (optional)
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Error distributions
        ax = axes[0, 0]
        normal_errors = reconstruction_errors[y_true == 0]
        threat_errors = reconstruction_errors[y_true == 1]
        
        ax.hist(normal_errors, bins=50, alpha=0.7, label='Normal', edgecolor='black')
        ax.hist(threat_errors, bins=50, alpha=0.7, label='Threat', edgecolor='black')
        ax.set_xlabel('Reconstruction Error')
        ax.set_ylabel('Frequency')
        ax.set_title('Error Distribution by Class')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # 2. Precision-Recall curve
        ax = axes[0, 1]
        precision, recall, thresholds = precision_recall_curve(y_true, reconstruction_errors)
        
        ax.plot(recall, precision, linewidth=2)
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.set_title('Precision-Recall Curve')
        ax.grid(alpha=0.3)
        
        # Mark optimal points
        if hasattr(self, 'results') and self.results:
            for name, result in self.results.items():
                if name in ['recall_optimized', 'precision_optimized', 'f1_optimized']:
                    ax.plot(result['recall'], result['precision'], 'ro', markersize=8)
                    ax.annotate(name.replace('_', ' '), 
                               (result['recall'], result['precision']),
                               xytext=(5, 5), textcoords='offset points')
        
        # 3. ROC curve
        ax = axes[1, 0]
        fpr, tpr, _ = roc_curve(y_true, reconstruction_errors)
        roc_auc = auc(fpr, tpr)
        
        ax.plot(fpr, tpr, linewidth=2, label=f'ROC (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curve')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # 4. F1 vs Threshold
        ax = axes[1, 1]
        precision, recall, thresholds = precision_recall_curve(y_true, reconstruction_errors)
        f1_scores = 2 * precision * recall / (precision + recall + 1e-10)
        
        ax.plot(thresholds, f1_scores[:-1], linewidth=2, label='F1 Score')
        ax.plot(thresholds, precision[:-1], linewidth=2, alpha=0.5, label='Precision')
        ax.plot(thresholds, recall[:-1], linewidth=2, alpha=0.5, label='Recall')
        ax.set_xlabel('Threshold')
        ax.set_ylabel('Score')
        ax.set_title('Metrics vs Threshold')
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"💾 Saved threshold analysis to {save_path}")
        
        plt.show()
    
    def recommend_threshold(self, use_case: str = 'healthcare') -> Dict:
        """
        Recommend threshold based on use case.
        
        Args:
            use_case: 'healthcare', 'finance', 'general'
        
        Returns:
            Recommended threshold config
        """
        if not self.results:
            raise ValueError("Must run find_optimal_threshold() first")
        
        recommendations = {
            'healthcare': {
                # Prioritize recall (catch all threats)
                'primary': self.results.get('recall_optimized', self.results.get('p95')),
                'rationale': 'Healthcare prioritizes catching all insider threats due to HIPAA/PHI sensitivity',
                'alert_threshold': 'p95',  # Alert on p95+
                'critical_threshold': 'p99'  # Critical alerts on p99+
            },
            'finance': {
                # Balance precision and recall
                'primary': self.results.get('f1_optimized', self.results.get('p95')),
                'rationale': 'Financial services balance false positives with threat detection',
                'alert_threshold': 'f1_optimized',
                'critical_threshold': 'p99'
            },
            'general': {
                # Optimize F1
                'primary': self.results.get('f1_optimized', self.results.get('p95')),
                'rationale': 'General use case optimizes for balanced performance',
                'alert_threshold': 'f1_optimized',
                'critical_threshold': 'p99'
            }
        }
        
        if use_case not in recommendations:
            use_case = 'general'
        
        recommendation = recommendations[use_case]
        
        print(f"\n📋 Recommended Configuration for {use_case.upper()}:")
        print(f"   Rationale: {recommendation['rationale']}")
        print(f"   Primary threshold: {recommendation['primary']['threshold']:.6f}")
        print(f"   Expected precision: {recommendation['primary']['precision']:.4f}")
        print(f"   Expected recall: {recommendation['primary']['recall']:.4f}")
        print(f"   Expected F1: {recommendation['primary']['f1']:.4f}")
        
        return recommendation


def compute_per_user_thresholds(reconstruction_errors: Dict[str, np.ndarray],
                               multiplier: float = 2.0) -> Dict[str, float]:
    """
    Compute per-user dynamic thresholds.
    
    Args:
        reconstruction_errors: Dict of user_id -> array of reconstruction errors
        multiplier: Std deviation multiplier
    
    Returns:
        Dict of user_id -> threshold
    """
    thresholds = {}
    
    for user_id, errors in reconstruction_errors.items():
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        threshold = mean_error + multiplier * std_error
        
        thresholds[user_id] = {
            'threshold': float(threshold),
            'mean': float(mean_error),
            'std': float(std_error),
            'p95': float(np.percentile(errors, 95)),
            'p99': float(np.percentile(errors, 99))
        }
    
    print(f"✅ Computed thresholds for {len(thresholds)} users")
    
    return thresholds


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("THRESHOLD TUNING DEMO")
    print("="*80)
    
    # Generate synthetic data for demo
    np.random.seed(42)
    
    # Normal behavior: low reconstruction error
    normal_errors = np.random.gamma(2, 0.002, 900)
    
    # Threats: high reconstruction error
    threat_errors = np.random.gamma(5, 0.008, 100)
    
    # Combine
    reconstruction_errors = np.concatenate([normal_errors, threat_errors])
    y_true = np.concatenate([np.zeros(900), np.ones(100)])
    
    # Shuffle
    indices = np.random.permutation(len(y_true))
    reconstruction_errors = reconstruction_errors[indices]
    y_true = y_true[indices]
    
    print(f"\n📊 Demo Data:")
    print(f"   Total samples: {len(y_true):,}")
    print(f"   Normal: {np.sum(y_true == 0):,}")
    print(f"   Threats: {np.sum(y_true == 1):,}")
    
    # Tune thresholds
    tuner = ThresholdTuner()
    
    results = tuner.find_optimal_threshold(
        y_true,
        reconstruction_errors,
        target_recall=0.95,
        target_precision=0.80
    )
    
    # Get recommendation
    recommendation = tuner.recommend_threshold(use_case='healthcare')
    
    # Plot
    tuner.plot_threshold_analysis(
        y_true,
        reconstruction_errors,
        save_path='threshold_analysis.png'
    )
    
    print("\n✅ Threshold tuning complete!")
