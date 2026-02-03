"""
Database operations for logging decisions
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List


class DecisionLogger:
    def __init__(self, db_path: str = "storage/logs.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create the decisions table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ai_output TEXT NOT NULL,
                task_context TEXT NOT NULL,
                policy_mode TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_flags TEXT NOT NULL,
                explanation TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                human_action TEXT,
                human_notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_decision(self, ai_output: str, task_context: str, policy_mode: str, 
                     decision_data: Dict[str, Any]) -> int:
        """
        Log a decision to the database
        
        Returns:
            The ID of the logged decision
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO decisions 
            (timestamp, ai_output, task_context, policy_mode, decision, confidence, 
             risk_flags, explanation, recommended_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            ai_output,
            task_context,
            policy_mode,
            decision_data["decision"],
            decision_data["confidence"],
            json.dumps(decision_data["risk_flags"]),
            decision_data["explanation"],
            decision_data["recommended_action"]
        ))
        
        decision_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return decision_id
    
    def update_human_action(self, decision_id: int, action: str, notes: str = ""):
        """Update a decision with human action (approve/reject)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE decisions 
            SET human_action = ?, human_notes = ?
            WHERE id = ?
        """, (action, notes, decision_id))
        
        conn.commit()
        conn.close()
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decisions from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM decisions 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        decisions = []
        
        for row in cursor.fetchall():
            decision = dict(zip(columns, row))
            decision["risk_flags"] = json.loads(decision["risk_flags"])
            decisions.append(decision)
        
        conn.close()
        return decisions