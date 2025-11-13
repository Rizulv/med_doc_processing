"""
MedicalDocAI - Architecture Diagram Generator
Generates a detailed system architecture diagram
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.lines as mlines

# Set up the figure with high DPI for detailed output
fig, ax = plt.subplots(figsize=(20, 24), dpi=150)
ax.set_xlim(0, 20)
ax.set_ylim(0, 24)
ax.axis('off')

# Color scheme
color_user = '#E8F4F8'
color_frontend = '#A8D5E2'
color_backend = '#76B6C4'
color_ai = '#1E88E5'
color_storage = '#FFA726'
color_infra = '#66BB6A'
color_cicd = '#AB47BC'
color_k8s = '#326CE5'

# Title
ax.text(10, 23, 'MedicalDocAI - System Architecture',
        fontsize=28, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#1E88E5', edgecolor='black', linewidth=2, alpha=0.9))
ax.text(10, 22.3, 'AI-Powered Medical Document Processing Platform',
        fontsize=14, ha='center', style='italic')

# Layer 1: User Layer (Top)
y_user = 20.5
user_box = FancyBboxPatch((8, y_user), 4, 1.2, boxstyle="round,pad=0.1",
                          facecolor=color_user, edgecolor='black', linewidth=2)
ax.add_patch(user_box)
ax.text(10, y_user + 0.6, '👤 End Users', fontsize=14, fontweight='bold', ha='center')
ax.text(10, y_user + 0.2, '(Healthcare Providers, Medical Staff)', fontsize=10, ha='center')

# Arrow from user to internet
arrow1 = FancyArrowPatch((10, y_user), (10, y_user - 0.8),
                        arrowstyle='->', mutation_scale=30, linewidth=2.5, color='black')
ax.add_patch(arrow1)

# Layer 2: Internet/Load Balancer
y_lb = 18.5
lb_box = FancyBboxPatch((6.5, y_lb), 7, 1.5, boxstyle="round,pad=0.1",
                        facecolor=color_infra, edgecolor='black', linewidth=2)
ax.add_patch(lb_box)
ax.text(10, y_lb + 1, '☁️ AWS Elastic Load Balancer', fontsize=13, fontweight='bold', ha='center')
ax.text(10, y_lb + 0.6, 'Region: ap-south-1', fontsize=10, ha='center')
ax.text(10, y_lb + 0.2, 'URL: ad28ddbf3...elb.amazonaws.com', fontsize=9, ha='center', style='italic')

# Arrow from LB to Frontend
arrow2 = FancyArrowPatch((10, y_lb), (10, y_lb - 0.8),
                        arrowstyle='->', mutation_scale=30, linewidth=2.5, color='black')
ax.add_patch(arrow2)

# Layer 3: Frontend (Web Service)
y_frontend = 15.5
frontend_box = FancyBboxPatch((5, y_frontend), 10, 2, boxstyle="round,pad=0.15",
                              facecolor=color_frontend, edgecolor='black', linewidth=2.5)
ax.add_patch(frontend_box)
ax.text(10, y_frontend + 1.5, '🌐 Frontend Layer', fontsize=14, fontweight='bold', ha='center')

# Frontend components
frontend_components = [
    ('React 18 + TypeScript', y_frontend + 1.1),
    ('Vite Build Tool', y_frontend + 0.8),
    ('Nginx Reverse Proxy', y_frontend + 0.5),
    ('shadcn/ui Components', y_frontend + 0.2)
]
for comp, y_pos in frontend_components:
    ax.text(10, y_pos, f'• {comp}', fontsize=10, ha='center')

# Kubernetes service label
ax.text(15.5, y_frontend + 1, 'K8s Service:\nLoadBalancer\nReplicas: 2',
        fontsize=8, ha='center', style='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Arrow from Frontend to Backend
arrow3 = FancyArrowPatch((10, y_frontend), (10, y_frontend - 1.2),
                        arrowstyle='<->', mutation_scale=30, linewidth=2.5, color='black')
ax.add_patch(arrow3)
ax.text(11.2, y_frontend - 0.6, 'API Calls', fontsize=9, style='italic')

# Layer 4: Backend (API Service)
y_backend = 11.5
backend_box = FancyBboxPatch((5, y_backend), 10, 2.5, boxstyle="round,pad=0.15",
                             facecolor=color_backend, edgecolor='black', linewidth=2.5)
ax.add_patch(backend_box)
ax.text(10, y_backend + 2.1, '⚙️ Backend API Layer', fontsize=14, fontweight='bold', ha='center')

# Backend components
backend_components = [
    ('FastAPI Framework (Python 3.12)', y_backend + 1.7),
    ('Document Classification Service', y_backend + 1.3),
    ('ICD-10 Code Extraction Service', y_backend + 1.0),
    ('Summary Generation Service', y_backend + 0.7),
    ('Text Extraction (PDF/TXT)', y_backend + 0.4),
    ('Port: 8000', y_backend + 0.1)
]
for comp, y_pos in backend_components:
    ax.text(10, y_pos, f'• {comp}', fontsize=10, ha='center')

# Kubernetes service label for backend
ax.text(15.5, y_backend + 1.5, 'K8s Service:\nClusterIP\nReplicas: 2\nDNS: api.dev',
        fontsize=8, ha='center', style='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Layer 5: AI & Storage Layer
y_ai_storage = 8

# AI Service Box
ai_box = FancyBboxPatch((1, y_ai_storage), 6, 2.2, boxstyle="round,pad=0.15",
                        facecolor=color_ai, edgecolor='black', linewidth=2.5)
ax.add_patch(ai_box)
ax.text(4, y_ai_storage + 1.8, '🤖 AI Processing', fontsize=13, fontweight='bold', ha='center', color='white')
ai_items = [
    'Anthropic Claude Sonnet 4.5',
    'Prompt Caching (Ephemeral)',
    'Model: claude-4-5',
    '~2-5s Response Time'
]
for i, item in enumerate(ai_items):
    ax.text(4, y_ai_storage + 1.3 - (i * 0.3), f'• {item}', fontsize=9, ha='center', color='white')

# Arrow from backend to AI
arrow_ai = FancyArrowPatch((8, y_backend + 0.5), (6, y_ai_storage + 1.8),
                          arrowstyle='<->', mutation_scale=25, linewidth=2, color='black',
                          connectionstyle="arc3,rad=0.3")
ax.add_patch(arrow_ai)
ax.text(6.5, y_backend - 0.5, 'AI API\nCalls', fontsize=8, ha='center', style='italic')

# Storage Services
# SQLite
sqlite_box = FancyBboxPatch((8.5, y_ai_storage), 4.5, 1, boxstyle="round,pad=0.1",
                            facecolor=color_storage, edgecolor='black', linewidth=2)
ax.add_patch(sqlite_box)
ax.text(10.75, y_ai_storage + 0.7, '🗄️ SQLite Database', fontsize=11, fontweight='bold', ha='center')
ax.text(10.75, y_ai_storage + 0.3, '(Metadata, Results)', fontsize=9, ha='center')

# S3
s3_box = FancyBboxPatch((8.5, y_ai_storage - 1.3), 4.5, 1, boxstyle="round,pad=0.1",
                        facecolor=color_storage, edgecolor='black', linewidth=2)
ax.add_patch(s3_box)
ax.text(10.75, y_ai_storage - 0.6, '☁️ AWS S3', fontsize=11, fontweight='bold', ha='center')
ax.text(10.75, y_ai_storage - 1, 'Bucket: med-docs-dev', fontsize=9, ha='center')

# Arrows from backend to storage
arrow_sqlite = FancyArrowPatch((10, y_backend), (10.75, y_ai_storage + 1),
                              arrowstyle='<->', mutation_scale=25, linewidth=2, color='black')
ax.add_patch(arrow_sqlite)

arrow_s3 = FancyArrowPatch((10, y_backend), (10.75, y_ai_storage - 0.3),
                          arrowstyle='<->', mutation_scale=25, linewidth=2, color='black')
ax.add_patch(arrow_s3)

# Layer 6: Kubernetes/EKS Infrastructure
y_k8s = 5.5
k8s_box = FancyBboxPatch((2, y_k8s), 16, 1.8, boxstyle="round,pad=0.15",
                         facecolor=color_k8s, edgecolor='black', linewidth=2.5)
ax.add_patch(k8s_box)
ax.text(10, y_k8s + 1.4, '☸️ Kubernetes Infrastructure (AWS EKS)', fontsize=14, fontweight='bold', ha='center', color='white')
k8s_info = [
    'Cluster: med-doc-dev | Region: ap-south-1 | K8s Version: 1.28',
    'Node Group: standard-workers (t3.medium) | Min: 1, Max: 3, Current: 2',
    'Namespace: dev | Deployments: api, web | Services: ClusterIP, LoadBalancer'
]
for i, info in enumerate(k8s_info):
    ax.text(10, y_k8s + 0.9 - (i * 0.4), info, fontsize=9, ha='center', color='white')

# Layer 7: CI/CD Pipeline
y_cicd = 3
cicd_box = FancyBboxPatch((2, y_cicd), 16, 2, boxstyle="round,pad=0.15",
                          facecolor=color_cicd, edgecolor='black', linewidth=2.5)
ax.add_patch(cicd_box)
ax.text(10, y_cicd + 1.6, '🔄 CI/CD Pipeline (GitHub Actions)', fontsize=14, fontweight='bold', ha='center', color='white')

# CI/CD stages
cicd_stages = [
    ('1. Build Backend\nDocker Image', 3.5, y_cicd + 0.9),
    ('2. Build Frontend\nDocker Image', 6.5, y_cicd + 0.9),
    ('3. Push to ECR\n(Image Registry)', 9.5, y_cicd + 0.9),
    ('4. Deploy to EKS\n(Rolling Update)', 12.5, y_cicd + 0.9),
    ('5. Run Evals\n(Quality Gate)', 15.5, y_cicd + 0.9)
]

for stage, x_pos, y_pos in cicd_stages:
    stage_box = FancyBboxPatch((x_pos - 1.2, y_pos - 0.5), 2.4, 0.9, boxstyle="round,pad=0.08",
                               facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(stage_box)
    ax.text(x_pos, y_pos, stage, fontsize=7.5, ha='center', va='center', fontweight='bold')

    if x_pos < 15.5:
        arrow_cicd = FancyArrowPatch((x_pos + 1.2, y_pos), (x_pos + 1.8, y_pos),
                                    arrowstyle='->', mutation_scale=15, linewidth=2, color='white')
        ax.add_patch(arrow_cicd)

ax.text(10, y_cicd + 0.2, 'Trigger: Push to main branch | OIDC Auth | Automated Testing',
        fontsize=9, ha='center', color='white', style='italic')

# Arrow from CICD to K8s
arrow_cicd_k8s = FancyArrowPatch((10, y_cicd + 2), (10, y_k8s + 1.8),
                                arrowstyle='->', mutation_scale=30, linewidth=2.5, color='black',
                                linestyle='dashed')
ax.add_patch(arrow_cicd_k8s)

# Layer 8: Document Types & Features
y_features = 0.5
features_box = FancyBboxPatch((0.5, y_features), 8.5, 1.8, boxstyle="round,pad=0.1",
                              facecolor='#FFF9C4', edgecolor='black', linewidth=2)
ax.add_patch(features_box)
ax.text(4.75, y_features + 1.5, '📄 Supported Document Types', fontsize=12, fontweight='bold', ha='center')
doc_types = [
    '• COMPLETE BLOOD COUNT (CBC)',
    '• BASIC METABOLIC PANEL (BMP)',
    '• X-RAY Reports',
    '• CT Scan Reports',
    '• CLINICAL NOTES'
]
for i, doc_type in enumerate(doc_types):
    ax.text(4.75, y_features + 1.1 - (i * 0.2), doc_type, fontsize=8, ha='center')

# Key Features
key_features_box = FancyBboxPatch((10, y_features), 9.5, 1.8, boxstyle="round,pad=0.1",
                                  facecolor='#E1F5FE', edgecolor='black', linewidth=2)
ax.add_patch(key_features_box)
ax.text(14.75, y_features + 1.5, '✨ Key Features', fontsize=12, fontweight='bold', ha='center')
features = [
    '✓ Document Classification (5 types)',
    '✓ ICD-10 Code Extraction with Evidence',
    '✓ AI-Powered Summarization',
    '✓ Automated Quality Evaluation',
    '✓ 99.9% Uptime with Auto-scaling'
]
for i, feature in enumerate(features):
    ax.text(14.75, y_features + 1.1 - (i * 0.2), feature, fontsize=8, ha='center')

# Technology Stack Legend (Right Side)
legend_x = 0.5
legend_y = 16

ax.text(legend_x + 1, legend_y + 0.5, '🛠️ Tech Stack', fontsize=11, fontweight='bold')

tech_stack = [
    ('Frontend:', 'React, TypeScript, Vite'),
    ('Backend:', 'FastAPI, Python 3.12'),
    ('AI:', 'Claude Sonnet 4.5'),
    ('Storage:', 'S3, SQLite'),
    ('Container:', 'Docker, ECR'),
    ('Orchestration:', 'Kubernetes, EKS'),
    ('CI/CD:', 'GitHub Actions'),
    ('Cloud:', 'AWS (ap-south-1)')
]

for i, (label, value) in enumerate(tech_stack):
    y_pos = legend_y - (i * 0.25)
    ax.text(legend_x, y_pos, label, fontsize=8, fontweight='bold')
    ax.text(legend_x + 1, y_pos, value, fontsize=8)

# Metrics Box (Right Side)
metrics_x = 0.5
metrics_y = 13

ax.text(metrics_x + 1, metrics_y + 0.5, '📊 Performance', fontsize=11, fontweight='bold')

metrics = [
    ('Response Time:', '2-5 seconds'),
    ('Deployment:', '3-4 minutes'),
    ('Uptime:', '99.9%'),
    ('Replicas:', '2 per service'),
    ('Scalability:', '100s req/min'),
    ('Monthly Cost:', '~$160-170')
]

for i, (label, value) in enumerate(metrics):
    y_pos = metrics_y - (i * 0.25)
    ax.text(metrics_x, y_pos, label, fontsize=8, fontweight='bold')
    ax.text(metrics_x + 1.2, y_pos, value, fontsize=8)

# API Endpoints (Right Side)
api_x = 0.5
api_y = 10.5

ax.text(api_x + 1.2, api_y + 0.5, '🔌 API Endpoints', fontsize=11, fontweight='bold')

endpoints = [
    'GET /health',
    'POST /classify',
    'POST /extract-codes',
    'POST /summarize',
    'POST /pipeline',
    'GET /eval/quick',
    'GET /docs'
]

for i, endpoint in enumerate(endpoints):
    ax.text(api_x, api_y - (i * 0.2), endpoint, fontsize=7, family='monospace',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', alpha=0.7))

# Footer
footer_text = '© 2025 MedicalDocAI | Production Ready | Deployed on AWS EKS'
ax.text(10, 0.1, footer_text, fontsize=10, ha='center', style='italic',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#E0E0E0', alpha=0.8))

# Save the figure
plt.tight_layout()
plt.savefig('MedicalDocAI_Architecture.png', dpi=150, bbox_inches='tight', facecolor='white')
print("Architecture diagram generated successfully: MedicalDocAI_Architecture.png")
plt.close()
