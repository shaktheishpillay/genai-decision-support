"""
UI component for displaying decision results
"""

import streamlit as st
from typing import Dict, Any


def display_decision_card(decision_data: Dict[str, Any]):
    """
    Display a decision card with color-coded results
    
    Args:
        decision_data: Dictionary containing decision, confidence, risk_flags, etc.
    """
    
    decision = decision_data["decision"]
    confidence = decision_data["confidence"]
    risk_flags = decision_data["risk_flags"]
    explanation = decision_data["explanation"]
    recommended_action = decision_data["recommended_action"]
    
    # Color coding based on decision
    if decision == "APPROVE":
        color = "green"
        icon = "✅"
    elif decision == "REJECT":
        color = "red"
        icon = "❌"
    else:  # REVIEW_REQUIRED
        color = "orange"
        icon = "⚠️"
    
    # Display decision header
    st.markdown(f"### {icon} Decision: **{decision}**")
    
    # Display confidence
    st.metric("Confidence Score", f"{confidence:.0%}")
    
    # Display risk flags
    if risk_flags:
        st.markdown("**🚩 Risk Flags:**")
        for flag in risk_flags:
            st.markdown(f"- `{flag}`")
    else:
        st.success("No risk flags detected")
    
    # Display explanation
    st.markdown("**💡 Explanation:**")
    st.info(explanation)
    
    # Display recommended action
    st.markdown("**🎯 Recommended Action:**")
    st.warning(recommended_action)
    
    # Visual separator
    st.markdown("---")


def display_decision_summary(decision_data: Dict[str, Any]):
    """
    Display a compact summary of the decision
    """
    decision = decision_data["decision"]
    confidence = decision_data["confidence"]
    
    # Create columns for compact display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if decision == "APPROVE":
            st.success(f"✅ {decision}")
        elif decision == "REJECT":
            st.error(f"❌ {decision}")
        else:
            st.warning(f"⚠️ {decision}")
    
    with col2:
        st.metric("Confidence", f"{confidence:.0%}")
    
    with col3:
        risk_count = len(decision_data["risk_flags"])
        st.metric("Risk Flags", risk_count)