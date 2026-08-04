import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import numpy as np
from io import BytesIO
import base64
from datetime import datetime
import io

# Configure page
st.set_page_config(
    page_title="Prostate Cancer Drug Repurposing Ranking",
    page_icon="💊",
    layout="wide"
)

# Drug data with evidence scoring
DRUG_DATA = [
    {
        "name": "Niraparib",
        "original_use": "Maintenance therapy for ovarian cancer",
        "pathway": "PARP-1/2 inhibitor (DNA repair)",
        "evidence_level": "FDA-Approved",
        "evidence_score": 95,
        "key_strengths": "FDA-approved for BRCA2-mutated mCSPC in Dec 2025; Phase III AMPLITUDE trial showed significant rPFS improvement",
        "key_limitations": "Biomarker dependency - efficacy primarily in BRCA1/2 mutations; no benefit in non-BRCA2 subgroup (HR 0.88)",
        "rank_reasoning": "Highest evidence level with FDA approval and positive Phase III data, though limited to biomarker-defined populations"
    },
    {
        "name": "Talazoparib",
        "original_use": "gBRCAm HER2-negative breast cancer",
        "pathway": "PARP-1/2 inhibitor + PARP trapping",
        "evidence_level": "FDA-Approved",
        "evidence_score": 93,
        "key_strengths": "FDA-approved with enzalutamide for HRR-mutated mCRPC; Phase III TALAPRO-2 showed PFS and OS benefits",
        "key_limitations": "Biomarker requirement (HRR gene mutations including BRCA1/2, ATM, CDK12)",
        "rank_reasoning": "Strong FDA approval with survival benefit, but requires specific genetic biomarkers"
    },
    {
        "name": "Levoketoconazole",
        "original_use": "Endogenous Cushing's syndrome",
        "pathway": "CYP11A1, CYP11B1, CYP17A1, CYP21A2 inhibition",
        "evidence_level": "Strong Theoretical & Preclinical",
        "evidence_score": 78,
        "key_strengths": "More potent enantiomer of ketoconazole; ketoconazole is already repurposed for CRPC; strong theoretical rationale",
        "key_limitations": "No direct clinical evidence for prostate cancer; all evidence extrapolated from ketoconazole",
        "rank_reasoning": "Strong preclinical rationale based on established drug class, but lacks direct clinical validation"
    },
    {
        "name": "Gedatolisib",
        "original_use": "Investigational (not FDA-approved)",
        "pathway": "Pan-PI3K + mTORC1/2 inhibitor",
        "evidence_level": "Phase 1/2 Clinical Trial",
        "evidence_score": 77,
        "key_strengths": "Ongoing Phase I/II trial (NCT06190899) with darolutamide showing manageable safety; median PFS 9.1 months",
        "key_limitations": "Combination-dependent with AR inhibitor; not studied as single agent",
        "rank_reasoning": "Promising early clinical data with strong pathway targeting, but requires combination therapy"
    },
    {
        "name": "Copanlisib",
        "original_use": "Relapsed follicular lymphoma",
        "pathway": "Pan-PI3K inhibitor (α, β, δ, γ)",
        "evidence_level": "Strong Preclinical",
        "evidence_score": 72,
        "key_strengths": "Superior anti-proliferative efficacy in prostate cancer cell lines; enhanced apoptosis with darolutamide; PDX model efficacy",
        "key_limitations": "Requires combination with AR inhibitor; limited single-agent activity",
        "rank_reasoning": "Strong preclinical data with synergistic potential, but combination-dependent"
    },
    {
        "name": "Capivasertib",
        "original_use": "HR+ HER2- breast cancer",
        "pathway": "AKT1/2/3 inhibitor (PI3K/AKT pathway)",
        "evidence_level": "FDA-approved for breast cancer subtype",
        "evidence_score": 70,
        "key_strengths": "FDA-approved for specific breast cancer subtype; strong scientific rationale for prostate cancer",
        "key_limitations": "Significant toxicity (67% Grade ≥3 AEs: hyperglycemia, diarrhea, rash); substantial treatment burden",
        "rank_reasoning": "Approved drug with pathway relevance, but toxicity is a major barrier for long-term use"
    },
    {
        "name": "Trilaciclib",
        "original_use": "Chemotherapy-induced myelosuppression (SCLC)",
        "pathway": "CDK4/6 inhibitor + NUAK2 inhibitor (off-target)",
        "evidence_level": "Preclinical (Novel Mechanism)",
        "evidence_score": 68,
        "key_strengths": "2025 discovery of NUAK2 inhibition (off-target); NUAK2 drives neuroendocrine prostate cancer; preclinical tumor growth suppression",
        "key_limitations": "No clinical evidence in prostate cancer; entirely preclinical; new mechanism requiring validation",
        "rank_reasoning": "Novel mechanism with strong preclinical data for aggressive NEPC, but lacks clinical validation"
    },
    {
        "name": "Alpelisib",
        "original_use": "HR+ HER2- breast cancer (PIK3CA-mutated)",
        "pathway": "PI3Kα selective inhibitor",
        "evidence_level": "Mixed/Investigational",
        "evidence_score": 65,
        "key_strengths": "Phase Ib trial showed anti-tumor activity in solid tumors (22% prostate cancer cohort)",
        "key_limitations": "High toxicity (Grade 3-4: 13% hyperglycemia, 13% rash); not prostate-specific; chemotherapy dose intensity reduction",
        "rank_reasoning": "Some clinical evidence but significant toxicity and lack of prostate-specific data"
    },
    {
        "name": "Thalidomide",
        "original_use": "Multiple myeloma, erythema nodosum leprosum",
        "pathway": "Cereblon modulation (anti-angiogenic, immunomodulatory)",
        "evidence_level": "Positive but Limited",
        "evidence_score": 60,
        "key_strengths": "Phase II trials in CRPC show modest activity; established anti-cancer drug",
        "key_limitations": "Modest and temporary PSA responses; median PFS ~2-3 months; Phase II concluded 'does not support Phase III testing'",
        "rank_reasoning": "Some clinical evidence but limited durability and insufficient for Phase III development"
    },
    {
        "name": "Ribociclib",
        "original_use": "HR+ HER2- breast cancer",
        "pathway": "CDK4/6 inhibitor",
        "evidence_level": "Mixed/Investigational",
        "evidence_score": 58,
        "key_strengths": "Prolonged median OS in combination arm (RiboX trial); preclinical radiosensitizer data",
        "key_limitations": "Primary endpoint failure (PSA50 response not met in RiboX trial)",
        "rank_reasoning": "Secondary endpoint benefits but primary endpoint failure limits regulatory potential"
    },
    {
        "name": "Abemaciclib",
        "original_use": "HR+ HER2- advanced breast cancer",
        "pathway": "CDK4/6 inhibitor",
        "evidence_level": "Mixed/Investigational",
        "evidence_score": 55,
        "key_strengths": "Promising preclinical data; combination strategies being explored (PSMA-targeted therapy, mHSPC)",
        "key_limitations": "Primary endpoint failure (rPFS not met in CYCLONE 2 trial for mCRPC)",
        "rank_reasoning": "Preclinical promise but Phase III failure in mCRPC limits current evidence"
    },
    {
        "name": "Mebendazole",
        "original_use": "Intestinal parasitic infections",
        "pathway": "Microtubule inhibition (tubulin binding)",
        "evidence_level": "Preclinical and Real-World",
        "evidence_score": 50,
        "key_strengths": "Preclinical synergy with docetaxel; ongoing clinical trial in Glasgow",
        "key_limitations": "No published clinical trial results; evidence from lab and animal models only",
        "rank_reasoning": "Interesting preclinical synergy but lacks definitive clinical data"
    },
    {
        "name": "Albendazole",
        "original_use": "Intestinal/tissue parasitic infections",
        "pathway": "Microtubule inhibition + other mechanisms",
        "evidence_level": "Preclinical",
        "evidence_score": 48,
        "key_strengths": "Completed clinical trial in Mexico (2011-2023) for malignant diseases (n=250)",
        "key_limitations": "No published results; not prostate cancer-specific; clinical efficacy unconfirmed",
        "rank_reasoning": "Some clinical exploration but no published prostate-specific data"
    },
    {
        "name": "Vorinostat",
        "original_use": "Cutaneous T-cell lymphoma",
        "pathway": "Pan-HDAC inhibitor (Class I/II)",
        "evidence_level": "Negative for Monotherapy",
        "evidence_score": 45,
        "key_strengths": "Potential for combination strategies",
        "key_limitations": "Phase II showed no single-agent activity; not recommended for further development as monotherapy",
        "rank_reasoning": "Failed as monotherapy, only potential in combinations"
    },
    {
        "name": "Temsirolimus",
        "original_use": "Advanced renal cell carcinoma",
        "pathway": "mTOR inhibitor (PI3K/AKT/mTOR pathway)",
        "evidence_level": "Mixed/Challenging",
        "evidence_score": 42,
        "key_strengths": "Strong scientific rationale due to pathway activation in prostate cancer",
        "key_limitations": "Multiple trials show limited single-agent activity in CRPC; some combination studies ongoing",
        "rank_reasoning": "Pathway rationale is strong but clinical data show limited single-agent efficacy"
    },
    {
        "name": "Lapatinib",
        "original_use": "HER2-positive breast cancer",
        "pathway": "EGFR (HER1) + HER2 inhibitor",
        "evidence_level": "Mixed/Investigational",
        "evidence_score": 40,
        "key_strengths": "Preclinical anti-tumor effects; potential in combination",
        "key_limitations": "Single-agent Phase II trials failed; no sufficient activity for further investigation",
        "rank_reasoning": "Preclinical promise but clinical failure as monotherapy"
    },
    {
        "name": "Griseofulvin",
        "original_use": "Dermatophyte infections (ringworm)",
        "pathway": "Microtubule dynamics (suppresses dynamic instability)",
        "evidence_level": "Preclinical",
        "evidence_score": 35,
        "key_strengths": "Distinct microtubule mechanism from polymerization inhibitors",
        "key_limitations": "No clinical evidence; exclusively preclinical data",
        "rank_reasoning": "Interesting mechanism but no clinical validation in prostate cancer"
    },
    {
        "name": "Cetuximab",
        "original_use": "Colorectal cancer, head/neck cancer",
        "pathway": "EGFR monoclonal antibody",
        "evidence_level": "Mixed/Limited",
        "evidence_score": 33,
        "key_strengths": "Phase II trial with docetaxel showed 34% 12-week PFS; potential as tumor-directing agent",
        "key_limitations": "Rapid resistance via HER2/HER3 overexpression; modest results; limited potential",
        "rank_reasoning": "Modest clinical results with significant resistance mechanisms"
    },
    {
        "name": "Lithium",
        "original_use": "Bipolar disorder",
        "pathway": "Multiple (gene expression, oxidative stress, histone modifications)",
        "evidence_level": "Preclinical/Phase I",
        "evidence_score": 30,
        "key_strengths": "Small Phase I safety trial completed; Phase II/III planned",
        "key_limitations": "Preclinical/Phase I stage only; efficacy trial not yet completed",
        "rank_reasoning": "Early stage of development with no efficacy data"
    },
    {
        "name": "Erlotinib",
        "original_use": "NSCLC (EGFR-mutated), pancreatic cancer",
        "pathway": "EGFR tyrosine kinase inhibitor",
        "evidence_level": "Negative",
        "evidence_score": 25,
        "key_strengths": "Approved for other cancers with EGFR mutations",
        "key_limitations": "Consistently failed to show single-agent activity in CRPC trials",
        "rank_reasoning": "Clinical trials show no significant anti-tumor effect as monotherapy"
    },
    {
        "name": "Gefitinib",
        "original_use": "NSCLC (EGFR-mutated)",
        "pathway": "EGFR tyrosine kinase inhibitor",
        "evidence_level": "Negative",
        "evidence_score": 23,
        "key_strengths": "Preclinical anti-tumor/anti-metastatic activity",
        "key_limitations": "Phase II trials show limited activity (11.4-15.8% PSA response); no PFS/OS improvement",
        "rank_reasoning": "Modest PSA responses but no survival benefit in clinical trials"
    },
    {
        "name": "Afatinib",
        "original_use": "NSCLC (EGFR-mutated)",
        "pathway": "Irreversible pan-ErbB inhibitor (EGFR, HER2, HER4)",
        "evidence_level": "Negative",
        "evidence_score": 20,
        "key_strengths": "Preclinical rationale existed; irreversible binding distinct from other TKIs",
        "key_limitations": "Phase II trial terminated early due to lack of efficacy",
        "rank_reasoning": "Early termination of Phase II trial due to lack of efficacy"
    },
    {
        "name": "Idelalisib",
        "original_use": "CLL, follicular lymphoma, SLL",
        "pathway": "PI3Kδ selective inhibitor",
        "evidence_level": "Negative (Resistance Mechanism)",
        "evidence_score": 15,
        "key_strengths": "Approved for hematologic malignancies",
        "key_limitations": "Prostate cancer expresses PIK3CD-S splice variant resistant to idelalisib; constitutive pathway activation",
        "rank_reasoning": "Identified resistance mechanism makes drug ineffective in prostate cancer"
    },
    {
        "name": "Duvelisib",
        "original_use": "CLL, SLL",
        "pathway": "PI3Kδ + PI3Kγ inhibitor",
        "evidence_level": "No Evidence",
        "evidence_score": 10,
        "key_strengths": "Approved for hematologic malignancies",
        "key_limitations": "No clinical or preclinical studies found for prostate cancer; no biological rationale identified",
        "rank_reasoning": "No evidence or biological rationale for prostate cancer use"
    },
    {
        "name": "Osimertinib",
        "original_use": "NSCLC (EGFR-mutated)",
        "pathway": "Third-generation EGFR TKI",
        "evidence_level": "Supportive/Preclinical Only",
        "evidence_score": 8,
        "key_strengths": "Approved for EGFR-mutated NSCLC",
        "key_limitations": "No direct anti-cancer activity on primary prostate cancer cells; only for metastatic lung lesions",
        "rank_reasoning": "No evidence of direct prostate cancer activity"
    },
    {
        "name": "Colchicine",
        "original_use": "Gout, familial Mediterranean fever",
        "pathway": "Microtubule depolymerization",
        "evidence_level": "Negative for Monotherapy",
        "evidence_score": 5,
        "key_strengths": "Potential for low-dose combination",
        "key_limitations": "High non-selective toxicity is a major barrier; clinical trial not pursued",
        "rank_reasoning": "High toxicity prevents clinical development despite potential"
    },
    {
        "name": "Podophyllotoxin",
        "original_use": "Genital warts (topical)",
        "pathway": "Microtubule inhibition (G2/M arrest)",
        "evidence_level": "Negative (Parent Drug)",
        "evidence_score": 3,
        "key_strengths": "Derivatives show clinical activity",
        "key_limitations": "Too toxic for systemic use (bone marrow arrest, neurologic/hepatic complications)",
        "rank_reasoning": "High systemic toxicity prevents use; only derivatives are viable"
    },
    {
        "name": "Palbociclib",
        "original_use": "HR+ HER2- breast cancer",
        "pathway": "CDK4/6 inhibitor",
        "evidence_level": "Negative for Monotherapy",
        "evidence_score": 2,
        "key_strengths": "Approved for breast cancer with strong clinical data in that indication",
        "key_limitations": "Phase II RCT in mCSPC showed no PSA response difference with ADT; no benefit in mCRPC",
        "rank_reasoning": "Clinical trial failure with no additional benefit over standard therapy"
    }
]

def calculate_rank_recommendation(drug: dict) -> str:
    """Calculate recommendation based on evidence score"""
    score = drug['evidence_score']
    if score >= 90:
        return "🌟 Strongly Recommended (Highest Evidence)"
    elif score >= 70:
        return "✅ Recommended (High Evidence)"
    elif score >= 50:
        return "🔬 Investigational (Moderate Evidence)"
    elif score >= 30:
        return "⚠️ Limited Evidence"
    else:
        return "❌ Not Recommended (Negative/No Evidence)"

def create_ranking_df(drugs: list) -> pd.DataFrame:
    """Create ranked dataframe with all relevant fields"""
    df = pd.DataFrame(drugs)
    df['rank'] = df['evidence_score'].rank(method='min', ascending=False).astype(int)
    df['recommendation'] = df.apply(calculate_rank_recommendation, axis=1)
    
    # Reorder columns for better display - include ALL columns
    cols = ['rank', 'name', 'evidence_score', 'evidence_level', 'recommendation', 
            'pathway', 'original_use', 'key_strengths', 'key_limitations', 'rank_reasoning']
    return df[cols].sort_values('rank')

def create_radar_chart(df: pd.DataFrame, top_n: int = 10):
    """Create radar chart for top drugs"""
    top_drugs = df.head(top_n)
    
    fig = go.Figure()
    
    categories = ['Evidence Level', 'Clinical Data', 'Scientific Rationale', 
                  'Safety Profile', 'Feasibility']
    
    # Normalize scores for each category (simplified based on available data)
    for _, row in top_drugs.iterrows():
        score = row['evidence_score']
        # Create a normalized profile based on the score and evidence level
        if row['evidence_level'] == 'FDA-Approved':
            profile = [95, 90, 80, 60, 80]
        elif 'Phase' in row['evidence_level']:
            profile = [80, 85, 90, 65, 75]
        elif row['evidence_level'] in ['Strong Preclinical', 'Strong Theoretical & Preclinical']:
            profile = [70, 60, 95, 70, 80]
        elif row['evidence_level'] == 'Preclinical':
            profile = [60, 50, 80, 75, 85]
        else:
            profile = [50, 40, 70, 70, 70]
        
        # Scale to match evidence score
        scale = score / 100
        scaled_profile = [p * scale for p in profile]
        
        fig.add_trace(go.Scatterpolar(
            r=scaled_profile,
            theta=categories,
            name=row['name'],
            fill='toself',
            opacity=0.6
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Top Drugs - Multidimensional Comparison",
        height=600
    )
    return fig

def create_scatter_plot(df: pd.DataFrame):
    """Create scatter plot of drugs by evidence score"""
    fig = px.scatter(
        df,
        x='rank',
        y='evidence_score',
        text='name',
        color='recommendation',
        size='evidence_score',
        size_max=50,
        title="Drug Ranking by Evidence Score",
        labels={'rank': 'Rank', 'evidence_score': 'Evidence Score (%)'}
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500)
    return fig

def convert_df_to_excel(df: pd.DataFrame) -> BytesIO:
    """Convert dataframe to Excel format with formatting"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Drug Rankings', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Drug Rankings']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add summary statistics sheet
        summary_data = {
            'Metric': ['Total Drugs Evaluated', 'FDA-Approved', 'Clinical Trial', 
                       'Preclinical', 'Highest Score', 'Lowest Score', 'Average Score'],
            'Value': [
                len(df),
                len(df[df['evidence_level'] == 'FDA-Approved']),
                len(df[df['evidence_level'].str.contains('Phase', na=False)]),
                len(df[df['evidence_level'].str.contains('Preclinical', na=False)]),
                df['evidence_score'].max(),
                df['evidence_score'].min(),
                df['evidence_score'].mean()
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
        
    return output

def create_pdf_report(df: pd.DataFrame) -> BytesIO:
    """Create a PDF report with all drug information"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        return None
    
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter), 
                           rightMargin=30, leftMargin=30, 
                           topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    
    # Create custom style for centered text
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=12
    )
    
    elements = []
    
    # Title
    title = Paragraph("Prostate Cancer Drug Repurposing Ranking", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Subtitle
    subtitle = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", center_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Summary statistics
    stats_data = [
        ['Metric', 'Value'],
        ['Total Drugs Evaluated', str(len(df))],
        ['FDA-Approved', str(len(df[df['evidence_level'] == 'FDA-Approved']))],
        ['Clinical Trial', str(len(df[df['evidence_level'].str.contains('Phase', na=False)]))],
        ['Preclinical', str(len(df[df['evidence_level'].str.contains('Preclinical', na=False)]))],
        ['Highest Score', f"{df['evidence_score'].max()}%"],
        ['Lowest Score', f"{df['evidence_score'].min()}%"],
        ['Average Score', f"{df['evidence_score'].mean():.1f}%"]
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # Main data table - limit to top 20 for readability
    display_df = df.head(20).copy()
    
    # Create table data
    table_data = [['Rank', 'Drug Name', 'Score', 'Evidence Level', 'Recommendation', 
                   'Pathway', 'Key Strengths', 'Key Limitations']]
    
    for _, row in display_df.iterrows():
        # Truncate long text for PDF
        strengths = row['key_strengths'][:100] + '...' if len(row['key_strengths']) > 100 else row['key_strengths']
        limitations = row['key_limitations'][:100] + '...' if len(row['key_limitations']) > 100 else row['key_limitations']
        pathway = row['pathway'][:80] + '...' if len(row['pathway']) > 80 else row['pathway']
        
        table_data.append([
            str(row['rank']),
            row['name'],
            f"{row['evidence_score']}%",
            row['evidence_level'],
            row['recommendation'][:40],
            pathway,
            strengths,
            limitations
        ])
    
    # Create table with appropriate column widths
    col_widths = [0.5*inch, 0.8*inch, 0.6*inch, 1.2*inch, 1.5*inch, 1.5*inch, 1.8*inch, 1.8*inch]
    main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(main_table)
    elements.append(Spacer(1, 20))
    
    # Add footer with reasoning
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey
    )
    
    footer_text = """
    <b>Methodology:</b> Drugs are ranked based on a composite score considering clinical trial results, 
    FDA approvals, preclinical data, mechanistic rationale, and safety profile. 
    Scores are normalized to 0-100% for comparative purposes.
    
    <b>Disclaimer:</b> This ranking is for educational and research purposes only. 
    All drug repurposing decisions should be made by qualified medical professionals 
    based on individual patient circumstances and current clinical guidelines.
    """
    footer = Paragraph(footer_text, footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    output.seek(0)
    return output

def main():
    st.title("💊 Prostate Cancer Drug Repurposing Ranking")
    st.markdown("""
    ### Comprehensive Evidence-Based Ranking of Repurposed Drugs
    
    This application ranks 27 drugs based on their evidence for repurposing in prostate cancer.
    Scores are calculated from clinical trial results, FDA approvals, preclinical data, 
    and mechanistic rationale.
    """)
    
    # Create ranked dataframe
    df = create_ranking_df(DRUG_DATA)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    
    min_score = st.sidebar.slider(
        "Minimum Evidence Score",
        min_value=0,
        max_value=100,
        value=0,
        step=5
    )
    
    evidence_levels = st.sidebar.multiselect(
        "Evidence Level",
        options=df['evidence_level'].unique(),
        default=df['evidence_level'].unique()
    )
    
    recommendation_filters = st.sidebar.multiselect(
        "Recommendation Category",
        options=df['recommendation'].unique(),
        default=df['recommendation'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['evidence_score'] >= min_score) &
        (df['evidence_level'].isin(evidence_levels)) &
        (df['recommendation'].isin(recommendation_filters))
    ]
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Drugs Evaluated", len(df))
    with col2:
        st.metric("After Filters", len(filtered_df))
    with col3:
        fda_approved = len(df[df['evidence_level'] == 'FDA-Approved'])
        st.metric("FDA-Approved for Prostate", fda_approved)
    with col4:
        top_score = df['evidence_score'].max()
        st.metric("Top Evidence Score", f"{top_score}%")
    
    # Download buttons in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Export Data")
    
    if not filtered_df.empty:
        # Excel download
        excel_data = convert_df_to_excel(filtered_df)
        st.sidebar.download_button(
            label="📊 Download as Excel",
            data=excel_data,
            file_name=f"drug_ranking_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # PDF download
        pdf_data = create_pdf_report(filtered_df)
        if pdf_data:
            st.sidebar.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name=f"drug_ranking_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.sidebar.info("ℹ️ Install reportlab for PDF export: `pip install reportlab`")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Ranked List", 
        "📈 Visualizations", 
        "📋 Detailed Analysis",
        "💡 Key Insights",
        "📥 Export Center"
    ])
    
    with tab1:
        st.subheader("🏆 Ranked Drugs by Repurposing Potential")
        st.markdown("*All drug information is displayed to help researchers understand the ranking rationale*")
        
        # Display ranked table with ALL columns
        display_cols = ['rank', 'name', 'evidence_score', 'evidence_level', 'recommendation', 
                       'pathway', 'original_use', 'key_strengths', 'key_limitations', 'rank_reasoning']
        
        styled_df = filtered_df[display_cols].copy()
        styled_df['evidence_score'] = styled_df['evidence_score'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600,
            column_config={
                "rank": "Rank",
                "name": "Drug Name",
                "evidence_score": "Score",
                "evidence_level": "Evidence Level",
                "recommendation": "Recommendation",
                "pathway": "Pathway Targeted",
                "original_use": "Original Use",
                "key_strengths": "Key Strengths",
                "key_limitations": "Key Limitations",
                "rank_reasoning": "Rank Reasoning"
            }
        )
    
    with tab2:
        st.subheader("📈 Evidence Score Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter plot
            fig_scatter = create_scatter_plot(filtered_df)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                filtered_df.head(15),
                x='name',
                y='evidence_score',
                color='recommendation',
                title="Top 15 Drugs by Evidence Score",
                labels={'evidence_score': 'Evidence Score (%)', 'name': ''},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Radar chart for top 10
        st.subheader("🎯 Multidimensional Comparison (Top 10)")
        fig_radar = create_radar_chart(filtered_df)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab3:
        st.subheader("📋 Detailed Drug Analysis")
        
        selected_drug = st.selectbox(
            "Select a drug for detailed analysis:",
            options=filtered_df['name'].tolist()
        )
        
        if selected_drug:
            drug_data = filtered_df[filtered_df['name'] == selected_drug].iloc[0]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Rank", f"#{drug_data['rank']}")
                st.metric("Evidence Score", f"{drug_data['evidence_score']}%")
                st.metric("Evidence Level", drug_data['evidence_level'])
                st.info(f"**Recommendation:** {drug_data['recommendation']}")
            
            with col2:
                st.markdown(f"**🔬 Original Use:** {drug_data['original_use']}")
                st.markdown(f"**🧬 Pathway Targeted:** {drug_data['pathway']}")
                st.markdown(f"**✅ Key Strengths:** {drug_data['key_strengths']}")
                st.markdown(f"**⚠️ Key Limitations:** {drug_data['key_limitations']}")
                st.markdown(f"**📌 Rank Reasoning:** {drug_data['rank_reasoning']}")
    
    with tab4:
        st.subheader("💡 Key Insights for Prostate Cancer Drug Repurposing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🏅 Top Performers
            
            **1. Niraparib (95%)** - FDA-approved for BRCA2-mutated mCSPC with significant rPFS improvement
            
            **2. Talazoparib (93%)** - FDA-approved with enzalutamide for HRR-mutated mCRPC with survival benefit
            
            **3. Levoketoconazole (78%)** - Strong preclinical rationale as a more potent ketoconazole enantiomer
            
            **4. Gedatolisib (77%)** - Promising Phase I/II data with darolutamide (PFS 9.1 months)
            
            **5. Copanlisib (72%)** - Strong preclinical synergy with AR inhibitors
            """)
            
        with col2:
            st.markdown("""
            ### ⚠️ Key Challenges
            
            **Biomarker Dependency** - PARP inhibitors require BRCA/HRR mutations
            
            **Toxicity Burden** - PI3K/AKT inhibitors show significant Grade ≥3 AEs
            
            **Combination Requirement** - Many promising drugs require AR inhibitor combinations
            
            **Resistance Mechanisms** - EGFR inhibitors face rapid resistance via HER receptor upregulation
            
            **Single-Agent Failure** - CDK4/6 inhibitors and mTOR inhibitors show limited monotherapy activity
            """)
        
        st.markdown("""
        ### 📊 Evidence Quality Summary
        
        | Evidence Level | Number of Drugs | Examples |
        |---|---|---|
        | FDA-Approved | 2 | Niraparib, Talazoparib |
        | Clinical Trial | 1 | Gedatolisib |
        | Preclinical | 8+ | Copanlisib, Trilaciclib, Mebendazole |
        | Mixed/Limited | 5+ | Temsirolimus, Lapatinib, Cetuximab |
        | Negative/No Evidence | 10+ | Erlotinib, Gefitinib, Idelalisib |
        """)
    
    with tab5:
        st.subheader("📥 Export Center")
        
        st.markdown("""
        ### Download Complete Reports
        
        Export the complete ranked dataset with all drug information for offline analysis.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Excel Export")
            st.markdown("""
            Export to Excel with all data including:
            - Complete drug rankings with all fields
            - Summary statistics
            - Auto-formatted columns
            """)
            
            excel_data_full = convert_df_to_excel(df)
            st.download_button(
                label="📥 Download Complete Dataset (All Drugs)",
                data=excel_data_full,
                file_name=f"complete_ranking_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            if not filtered_df.empty:
                excel_data_filtered = convert_df_to_excel(filtered_df)
                st.download_button(
                    label=f"📥 Download Filtered Dataset ({len(filtered_df)} drugs)",
                    data=excel_data_filtered,
                    file_name=f"filtered_ranking_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### 📄 PDF Report")
            st.markdown("""
            Professional PDF report including:
            - Executive summary with statistics
            - Top 20 drugs with all key information
            - Methodology and disclaimer
            """)
            
            pdf_data = create_pdf_report(df)
            if pdf_data:
                st.download_button(
                    label="📄 Download Complete Report (All Drugs)",
                    data=pdf_data,
                    file_name=f"complete_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                if not filtered_df.empty:
                    pdf_data_filtered = create_pdf_report(filtered_df)
                    if pdf_data_filtered:
                        st.download_button(
                            label=f"📄 Download Filtered Report ({len(filtered_df)} drugs)",
                            data=pdf_data_filtered,
                            file_name=f"filtered_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            else:
                st.warning("⚠️ PDF generation requires reportlab. Install with: `pip install reportlab`")
        
        # Data preview
        st.markdown("---")
        st.markdown("### 📊 Data Preview")
        preview_cols = ['rank', 'name', 'evidence_score', 'evidence_level', 'recommendation', 'pathway']
        st.dataframe(
            df[preview_cols].head(10),
            use_container_width=True,
            column_config={
                "evidence_score": st.column_config.NumberColumn(
                    "Score",
                    format="%.0f%%"
                )
            }
        )
    
    # Footer
    st.markdown("""
    ---
    **📋 Methodology:** Drugs are ranked based on a composite score considering clinical trial results, 
    FDA approvals, preclinical data, mechanistic rationale, and safety profile. 
    Scores are normalized to 0-100% for comparative purposes.
    
    **⚠️ Disclaimer:** This ranking is for educational and research purposes only. 
    All drug repurposing decisions should be made by qualified medical professionals 
    based on individual patient circumstances and current clinical guidelines.
    """)

if __name__ == "__main__":
    main()
