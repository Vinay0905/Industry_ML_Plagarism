"""
Streamlit UI for Plagiarism Detection System
Visualizes the complete pipeline with logs, progress bars, and results table.
"""

import streamlit as st
import pandas as pd
import logging
import io
from itertools import combinations
from datetime import datetime
import json

from src.io import load_submissions
from src.fusion import PlagiarismScorer
from src.normalization import get_normalizer

# Configure page
st.set_page_config(
    page_title="Plagiarism Detection Pipeline",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .log-container {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        font-size: 12px;
        max-height: 400px;
        overflow-y: auto;
    }
    .stage-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'submissions' not in st.session_state:
    st.session_state.submissions = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Custom logging handler to capture logs
class StreamlitLogHandler(logging.Handler):
    def emit(self, record):
        try:
            # Only log if we have Streamlit context (not in background threads)
            if 'logs' in st.session_state:
                log_entry = self.format(record)
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.logs.append(f"[{timestamp}] {log_entry}")
        except (KeyError, AttributeError, RuntimeError):
            # Silently ignore if we're in a background thread without Streamlit context
            pass

# Setup logging
def setup_logging():
    """Configure logging to capture all messages."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add Streamlit handler
    handler = StreamlitLogHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Initialize logging
setup_logging()

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# CSV file path (hardcoded)
csv_path = st.sidebar.text_input(
    "CSV File Path",
    value="D:/vinay_programing/PR4/Industry_ML_Plagarism/Data/RAW/trapping_rain_water.csv"
)

# Analysis options
st.sidebar.subheader("Analysis Options")
use_semantic = st.sidebar.checkbox("Enable Semantic Analysis (CodeBERT)", value=False, 
                                   help="Disable for faster processing")
normalize_code = st.sidebar.checkbox("Normalize Code", value=True)

# Clear cache button
if st.sidebar.button("🗑️ Clear Cache & Reset"):
    st.session_state.clear()
    st.rerun()

# Main title
st.title("🔍 Plagiarism Detection Pipeline")
st.markdown("---")

# Run analysis button
if st.button("▶️ Run Analysis", type="primary", width="stretch"):
    st.session_state.logs = []
    st.session_state.processing_complete = False
    
    try:
        # ============================================================
        # STAGE 1: Data Loading
        # ============================================================
        st.markdown('<div class="stage-header"><h3>📂 Stage 1: Data Loading & Validation</h3></div>', 
                   unsafe_allow_html=True)
        
        stage1_progress = st.progress(0, text="Loading CSV file...")
        
        submissions = load_submissions(csv_path)
        st.session_state.submissions = submissions
        
        stage1_progress.progress(100, text=f"✓ Loaded {len(submissions)} submissions")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Submissions", len(submissions))
        with col2:
            languages = set(sub.get('language', 'unknown') for sub in submissions)
            st.metric("Languages", ", ".join(languages))
        with col3:
            total_pairs = len(submissions) * (len(submissions) - 1) // 2
            st.metric("Pairwise Comparisons", total_pairs)
        
        st.success(f"✅ Loaded {len(submissions)} submissions successfully!")
        
        # ============================================================
        # STAGE 2-6: Pairwise Analysis
        # ============================================================
        st.markdown('<div class="stage-header"><h3>🔬 Stages 2-6: Multi-Signal Analysis</h3></div>', 
                   unsafe_allow_html=True)
        
        st.info("""
        **Pipeline Stages per Comparison:**
        1. Code Normalization
        2. Lexical Analysis (TF-IDF, n-grams)
        3. Structural Analysis (AST with tree-sitter)
        4. Semantic Analysis (CodeBERT embeddings) - Optional
        5. Score Fusion with Student-Safe Bias
        """)
        
        # Initialize scorer
        scorer = PlagiarismScorer()
        
        # Optionally disable semantic analysis for speed
        if not use_semantic:
            scorer.semantic_analyzer.model = None
            st.warning("⚡ Semantic analysis disabled for faster processing")
        
        # Compute pairwise similarities
        results = []
        total_pairs = len(list(combinations(range(len(submissions)), 2)))
        
        analysis_progress = st.progress(0, text="Analyzing pairwise similarities...")
        
        for idx, (i, j) in enumerate(combinations(range(len(submissions)), 2)):
            sub_i = submissions[i]
            sub_j = submissions[j]
            
            # Update progress
            progress_pct = int((idx + 1) / total_pairs * 100)
            analysis_progress.progress(
                progress_pct, 
                text=f"Comparing {sub_i['submission_id']} vs {sub_j['submission_id']} ({idx+1}/{total_pairs})"
            )
            
            # Compute similarity
            result = scorer.compute_similarity(
                sub_i['code'],
                sub_j['code'],
                language=sub_i.get('language', 'python'),
                normalize=normalize_code
            )
            
            results.append({
                'Index_i': i,
                'Index_j': j,
                'Submission_1': sub_i['submission_id'],
                'Submission_2': sub_j['submission_id'],
                'Language': sub_i.get('language', 'python'),
                'Lexical_Sim_%': round(result['breakdown']['lexical'], 2),
                'Structural_Sim_%': round(result['breakdown']['structural'], 2),
                'Semantic_Sim_%': round(result['breakdown']['semantic'], 2) if use_semantic else None,
                'Overall_%': round(result['final_score'], 2),
                'Severity': result['severity'].upper(),
                'Structural_Method': result['structural_method']
            })
        
        analysis_progress.progress(100, text=f"✓ Completed {total_pairs} pairwise comparisons")
        
        # Create results DataFrame
        results_df = pd.DataFrame(results).sort_values('Overall_%', ascending=False)
        st.session_state.results_df = results_df
        st.session_state.processing_complete = True
        
        st.success("✅ Analysis complete!")
        
        # Summary statistics
        st.markdown('<div class="stage-header"><h3>📊 Summary Statistics</h3></div>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            severe_count = len(results_df[results_df['Severity'] == 'SEVERE'])
            st.metric("🚨 Severe Cases", severe_count, 
                     delta=f"{severe_count/len(results_df)*100:.1f}%")
        
        with col2:
            partial_count = len(results_df[results_df['Severity'] == 'PARTIAL'])
            st.metric("⚠️ Partial Cases", partial_count,
                     delta=f"{partial_count/len(results_df)*100:.1f}%")
        
        with col3:
            clean_count = len(results_df[results_df['Severity'] == 'CLEAN'])
            st.metric("✅ Clean Cases", clean_count,
                     delta=f"{clean_count/len(results_df)*100:.1f}%")
        
        with col4:
            avg_similarity = results_df['Overall_%'].mean()
            st.metric("Average Similarity", f"{avg_similarity:.1f}%")
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        logging.error(f"Analysis failed: {e}", exc_info=True)

# ============================================================
# RESULTS TABLE & CODE VIEWER
# ============================================================
if st.session_state.processing_complete and st.session_state.results_df is not None:
    st.markdown("---")
    st.markdown('<div class="stage-header"><h3>📋 Pairwise Comparison Results</h3></div>', 
               unsafe_allow_html=True)
    
    results_df = st.session_state.results_df
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=['SEVERE', 'PARTIAL', 'CLEAN'],
            default=['SEVERE', 'PARTIAL', 'CLEAN']
        )
    
    with col2:
        min_similarity = st.slider("Minimum Similarity %", 0, 100, 0)
    
    # Apply filters
    filtered_df = results_df[
        (results_df['Severity'].isin(severity_filter)) &
        (results_df['Overall_%'] >= min_similarity)
    ]
    
    # Display results table
    st.dataframe(
        filtered_df,
        width="stretch",
        height=400,
        column_config={
            "Overall_%": st.column_config.ProgressColumn(
                "Overall %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Lexical_Sim_%": st.column_config.NumberColumn("Lexical %", format="%.1f%%"),
            "Structural_Sim_%": st.column_config.NumberColumn("Structural %", format="%.1f%%"),
            "Semantic_Sim_%": st.column_config.NumberColumn("Semantic %", format="%.1f%%"),
        }
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name=f"plagiarism_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # ============================================================
    # CODE VIEWER
    # ============================================================
    st.markdown("---")
    st.markdown('<div class="stage-header"><h3>👀 Code Viewer</h3></div>', 
               unsafe_allow_html=True)
    
    st.info("Select a row number from the results table to view the code comparison")
    
    row_index = st.number_input(
        "Enter row number (0-indexed)",
        min_value=0,
        max_value=len(filtered_df)-1,
        value=0,
        step=1
    )
    
    if row_index < len(filtered_df):
        selected_row = filtered_df.iloc[row_index]
        
        idx_i = int(selected_row['Index_i'])
        idx_j = int(selected_row['Index_j'])
        
        submissions = st.session_state.submissions
        
        st.markdown(f"**Comparison:** `{selected_row['Submission_1']}` vs `{selected_row['Submission_2']}`")
        st.markdown(f"**Overall Similarity:** {selected_row['Overall_%']:.1f}% ({selected_row['Severity']})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 📄 {selected_row['Submission_1']}")
            st.code(submissions[idx_i]['code'], language=selected_row['Language'])
        
        with col2:
            st.markdown(f"### 📄 {selected_row['Submission_2']}")
            st.code(submissions[idx_j]['code'], language=selected_row['Language'])
        
        # Detailed breakdown
        st.markdown("#### Similarity Breakdown")
        breakdown_cols = st.columns(4)
        with breakdown_cols[0]:
            st.metric("Lexical", f"{selected_row['Lexical_Sim_%']:.1f}%")
        with breakdown_cols[1]:
            st.metric("Structural", f"{selected_row['Structural_Sim_%']:.1f}%")
        with breakdown_cols[2]:
            if selected_row['Semantic_Sim_%'] is not None:
                st.metric("Semantic", f"{selected_row['Semantic_Sim_%']:.1f}%")
            else:
                st.metric("Semantic", "N/A")
        with breakdown_cols[3]:
            st.metric("Method", selected_row['Structural_Method'])

# ============================================================
# LOGS VIEWER (Always visible)
# ============================================================
st.markdown("---")
st.markdown('<div class="stage-header"><h3>📝 Pipeline Logs</h3></div>', 
           unsafe_allow_html=True)

with st.expander("View Detailed Logs", expanded=False):
    if st.session_state.logs:
        log_text = "\n".join(st.session_state.logs[-100:])  # Show last 100 logs
        st.markdown(f'<div class="log-container">{log_text}</div>', 
                   unsafe_allow_html=True)
    else:
        st.info("No logs yet. Run the analysis to see logs.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Plagiarism Detection System | Built with Streamlit
</div>
""", unsafe_allow_html=True)
