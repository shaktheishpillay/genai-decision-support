"""
Main chat interface
"""

import streamlit as st
from core.evaluator import DecisionEvaluator
from storage.database import DecisionLogger
from ui.decision_card import display_decision_card


def render_chat_interface():
    """Render the main chat interface"""
    
    st.title("🤖 GenAI Decision Support System")
    st.markdown("**Human-in-the-Loop AI Governance**")
    st.markdown("---")
    
    # Initialize components
    if "evaluator" not in st.session_state:
        st.session_state.evaluator = DecisionEvaluator()
    
    if "logger" not in st.session_state:
        st.session_state.logger = DecisionLogger()
    
    # Sidebar for policy mode selection
    st.sidebar.header("⚙️ Configuration")
    policy_mode = st.sidebar.selectbox(
        "Policy Mode",
        ["strict", "balanced", "relaxed"],
        index=1,
        help="Strict = High caution | Balanced = Standard | Relaxed = Low risk tolerance"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Policy Modes")
    st.sidebar.markdown("""
    **Strict:** High-risk environment  
    Requires review for any uncertainty
    
    **Balanced:** Standard corporate  
    Balance safety with efficiency
    
    **Relaxed:** Low-risk environment  
    Only flag clear issues
    """)
    
    # Main input area
    st.header("📝 Submit AI Output for Review")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        task_context = st.text_input(
            "Task Context",
            placeholder="e.g., Customer support response, Financial recommendation, etc.",
            help="What was the AI trying to do?"
        )
    
    ai_output = st.text_area(
        "AI Output to Evaluate",
        height=200,
        placeholder="Paste the AI-generated output here...",
        help="The actual output from your AI system that needs governance review"
    )
    
    evaluate_button = st.button("🔍 Evaluate Output", type="primary", use_container_width=True)
    
    # Evaluation logic
    if evaluate_button:
        if not ai_output.strip():
            st.error("❌ Please provide an AI output to evaluate")
        elif not task_context.strip():
            st.error("❌ Please provide task context")
        else:
            with st.spinner("🤔 Evaluating AI output..."):
                try:
                    # Run evaluation
                    decision_data = st.session_state.evaluator.evaluate(
                        ai_output=ai_output,
                        task_context=task_context,
                        policy_mode=policy_mode
                    )
                    
                    # Log the decision
                    decision_id = st.session_state.logger.log_decision(
                        ai_output=ai_output,
                        task_context=task_context,
                        policy_mode=policy_mode,
                        decision_data=decision_data
                    )
                    
                    # Store in session state
                    st.session_state.current_decision = decision_data
                    st.session_state.current_decision_id = decision_id
                    
                    st.success("✅ Evaluation complete!")
                
                except Exception as e:
                    st.error(f"❌ Error during evaluation: {str(e)}")
    
    # Display results
    if "current_decision" in st.session_state:
        st.markdown("---")
        st.header("📊 Evaluation Results")
        
        display_decision_card(st.session_state.current_decision)
        
        # Human action buttons
        st.markdown("### 👤 Human Decision")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve", use_container_width=True):
                st.session_state.logger.update_human_action(
                    st.session_state.current_decision_id,
                    "APPROVED",
                    "Human reviewer approved this output"
                )
                st.success("✅ Output approved and logged!")
        
        with col2:
            if st.button("❌ Reject", use_container_width=True):
                st.session_state.logger.update_human_action(
                    st.session_state.current_decision_id,
                    "REJECTED",
                    "Human reviewer rejected this output"
                )
                st.error("❌ Output rejected and logged!")
        
        with col3:
            if st.button("🔄 Request Revision", use_container_width=True):
                st.session_state.logger.update_human_action(
                    st.session_state.current_decision_id,
                    "REVISION_REQUESTED",
                    "Human reviewer requested revisions"
                )
                st.warning("🔄 Revision requested and logged!")
    
    # Show recent decisions
    st.markdown("---")
    st.header("📜 Recent Decisions")
    
    recent_decisions = st.session_state.logger.get_recent_decisions(limit=5)
    
    if recent_decisions:
        for idx, decision in enumerate(recent_decisions):
            with st.expander(f"Decision #{decision['id']} - {decision['decision']} ({decision['timestamp'][:19]})"):
                st.markdown(f"**Task:** {decision['task_context']}")
                st.markdown(f"**Policy Mode:** `{decision['policy_mode']}`")
                st.markdown(f"**Confidence:** {decision['confidence']:.0%}")
                st.markdown(f"**Risk Flags:** {', '.join(decision['risk_flags']) if decision['risk_flags'] else 'None'}")
                if decision['human_action']:
                    st.markdown(f"**Human Action:** {decision['human_action']}")
    else:
        st.info("No decisions logged yet. Submit an AI output above to get started!")