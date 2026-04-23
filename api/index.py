from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy import text
from api.database import SessionLocal
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------- Dashboard ----------

@app.get("/")
def serve_dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "..", "public", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


# ---------- Models ----------

class StartEvent(BaseModel):
    user_id: str
    funnel_name: str
    step_name: str
    channel: str

class FunnelCreate(BaseModel):
    funnel_name: str
    description: str | None = None


# ---------- Helpers ----------

def build_date_params(base: dict, start_date: Optional[str], end_date: Optional[str]) -> dict:
    if start_date:
        base["start_date"] = start_date
    if end_date:
        base["end_date"] = end_date
    return base


# ---------- Health ----------

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# ---------- Events ----------

@app.post("/api/events/start")
def create_start_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'start', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/api/events/step")
def create_step_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'step', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "step event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/api/events/complete")
def create_complete_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'complete', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "complete event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/api/events/abandon")
def create_abandon_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'abandon', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "abandon event saved", "event_id": new_id}
    finally:
        db.close()


# ---------- Funnels ----------

@app.post("/api/funnels")
def create_funnel(funnel: FunnelCreate):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            INSERT INTO funnels (funnel_name, description)
            VALUES (:funnel_name, :description)
            RETURNING id, funnel_name, description, created_at;
        """), {"funnel_name": funnel.funnel_name, "description": funnel.description}).mappings().first()
        db.commit()
        return dict(result)
    finally:
        db.close()

@app.get("/api/funnels")
def get_funnels():
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT id, funnel_name, description, created_at
            FROM funnels ORDER BY id ASC;
        """)).mappings().all()
        return {"funnels": [dict(row) for row in result]}
    finally:
        db.close()

@app.get("/api/funnels/{funnel_id}")
def get_funnel_by_id(funnel_id: int):
    db = SessionLocal()
    try:
        funnel = db.execute(text("""
            SELECT id, funnel_name, description, created_at
            FROM funnels WHERE id = :funnel_id;
        """), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        steps = db.execute(text("""
            SELECT id, step_name, step_order, created_at
            FROM funnel_steps WHERE funnel_id = :funnel_id ORDER BY step_order;
        """), {"funnel_id": funnel_id}).mappings().all()
        return {"funnel": dict(funnel), "steps": [dict(s) for s in steps]}
    finally:
        db.close()


# ---------- Analytics ----------

@app.get("/api/analytics/funnel/{funnel_id}/steps")
def funnel_step_report(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        date_filter = ""
        if start_date:
            date_filter += " AND e.created_at >= :start_date"
        if end_date:
            date_filter += " AND e.created_at <= :end_date"
        params = build_date_params({"funnel_id": funnel_id}, start_date, end_date)
        rows = db.execute(text(f"""
            WITH step_users AS (
                SELECT fs.step_order, fs.step_name,
                    COUNT(DISTINCT e.user_id) AS users_at_step
                FROM funnel_steps fs
                LEFT JOIN events e
                    ON e.funnel_name = (SELECT funnel_name FROM funnels WHERE id = :funnel_id)
                    AND e.step_name = fs.step_name
                    {date_filter}
                WHERE fs.funnel_id = :funnel_id
                GROUP BY fs.step_order, fs.step_name
            )
            SELECT step_order, step_name, users_at_step,
                LAG(users_at_step) OVER (ORDER BY step_order) AS users_previous_step,
                CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                     ELSE LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step
                END AS drop_off_users,
                CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                     WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                     ELSE ROUND(((LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)::numeric
                          / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                END AS drop_off_percentage,
                CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                     WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                     ELSE ROUND((users_at_step::numeric / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                END AS conversion_rate_percentage
            FROM step_users ORDER BY step_order;
        """), params).mappings().all()
        return {"funnel_id": funnel_id, "funnel_name": funnel["funnel_name"], "steps": [dict(r) for r in rows]}
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/summary")
def funnel_summary(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        where_date_filter = ""
        join_date_filter = ""
        if start_date:
            where_date_filter += " AND created_at >= :start_date"
            join_date_filter += " AND e.created_at >= :start_date"
        if end_date:
            where_date_filter += " AND created_at <= :end_date"
            join_date_filter += " AND e.created_at <= :end_date"
        params = build_date_params(
            {"funnel_name": funnel_name, "funnel_id": funnel_id},
            start_date, end_date
        )
        total_started = db.execute(text(f"""
            SELECT COUNT(DISTINCT user_id) FROM events
            WHERE funnel_name = :funnel_name AND event_type = 'start' {where_date_filter};
        """), params).scalar() or 0
        total_completed = db.execute(text(f"""
            SELECT COUNT(DISTINCT user_id) FROM events
            WHERE funnel_name = :funnel_name AND event_type = 'complete' {where_date_filter};
        """), params).scalar() or 0
        overall_conversion = round((total_completed / total_started) * 100, 2) if total_started > 0 else None
        biggest_drop = db.execute(text(f"""
            WITH step_users AS (
                SELECT fs.step_order, fs.step_name,
                    COUNT(DISTINCT e.user_id) AS users_at_step
                FROM funnel_steps fs
                LEFT JOIN events e ON e.funnel_name = :funnel_name
                    AND e.step_name = fs.step_name {join_date_filter}
                WHERE fs.funnel_id = :funnel_id
                GROUP BY fs.step_order, fs.step_name
            ),
            step_metrics AS (
                SELECT step_order, step_name,
                    CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                         ELSE LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step
                    END AS drop_off_users,
                    CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                         WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                         ELSE ROUND(((LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)::numeric
                              / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                    END AS drop_off_percentage
                FROM step_users
            )
            SELECT step_order, step_name, drop_off_users, drop_off_percentage
            FROM step_metrics WHERE drop_off_percentage IS NOT NULL
            ORDER BY drop_off_percentage DESC LIMIT 1;
        """), params).mappings().first()
        return {
            "funnel_id": funnel_id, "funnel_name": funnel_name,
            "total_started": total_started, "total_completed": total_completed,
            "overall_conversion_percentage": overall_conversion,
            "biggest_drop_off_step": dict(biggest_drop) if biggest_drop else None
        }
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/time")
def funnel_time_analysis(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        date_filter = ""
        if start_date:
            date_filter += " AND created_at >= :start_date"
        if end_date:
            date_filter += " AND created_at <= :end_date"
        params = build_date_params(
            {"funnel_id": funnel_id, "funnel_name": funnel_name},
            start_date, end_date
        )
        rows = db.execute(text(f"""
            WITH ordered_steps AS (
                SELECT step_order, step_name,
                    LEAD(step_name) OVER (ORDER BY step_order) AS next_step_name,
                    LEAD(step_order) OVER (ORDER BY step_order) AS next_step_order
                FROM funnel_steps WHERE funnel_id = :funnel_id
            ),
            first_step_time AS (
                SELECT user_id, step_name, MIN(created_at) AS first_time
                FROM events WHERE funnel_name = :funnel_name {date_filter}
                GROUP BY user_id, step_name
            ),
            step_pairs AS (
                SELECT os.step_order, os.step_name, os.next_step_order, os.next_step_name,
                    fst1.user_id, fst1.first_time AS step_time, fst2.first_time AS next_step_time
                FROM ordered_steps os
                JOIN first_step_time fst1 ON fst1.step_name = os.step_name
                JOIN first_step_time fst2 ON fst2.step_name = os.next_step_name AND fst2.user_id = fst1.user_id
                WHERE os.next_step_name IS NOT NULL
            )
            SELECT step_order, step_name, next_step_order, next_step_name,
                COUNT(*) AS users_with_both_steps,
                ROUND(AVG(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS avg_minutes_to_next_step,
                ROUND(MIN(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS min_minutes_to_next_step,
                ROUND(MAX(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS max_minutes_to_next_step
            FROM step_pairs WHERE next_step_time >= step_time
            GROUP BY step_order, step_name, next_step_order, next_step_name
            ORDER BY step_order;
        """), params).mappings().all()
        time_analysis = [dict(r) for r in rows]
        slowest = max(time_analysis, key=lambda x: x["avg_minutes_to_next_step"] or -1) if time_analysis else None
        return {
            "funnel_id": funnel_id, "funnel_name": funnel_name,
            "slowest_transition": slowest, "time_analysis": time_analysis
        }
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/channel")
def funnel_channel_breakdown(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        date_filter = ""
        if start_date:
            date_filter += " AND created_at >= :start_date"
        if end_date:
            date_filter += " AND created_at <= :end_date"
        params = build_date_params(
            {"funnel_name": funnel_name, "funnel_id": funnel_id},
            start_date, end_date
        )
        rows = db.execute(text(f"""
            WITH channel_stats AS (
                SELECT
                    channel,
                    COUNT(DISTINCT user_id) FILTER (WHERE event_type = 'start') AS started,
                    COUNT(DISTINCT user_id) FILTER (WHERE event_type = 'complete') AS completed
                FROM events
                WHERE funnel_name = :funnel_name {date_filter}
                GROUP BY channel
            )
            SELECT channel, started, completed,
                CASE WHEN started = 0 THEN NULL
                     ELSE ROUND((completed::numeric / started) * 100, 2)
                END AS conversion_rate
            FROM channel_stats ORDER BY started DESC;
        """), params).mappings().all()
        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "channels": [dict(r) for r in rows]
        }
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/users")
def funnel_user_drilldown(
    funnel_id: int,
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        where_date_filter = ""
        e_date_filter = ""
        if start_date:
            where_date_filter += " AND created_at >= :start_date"
            e_date_filter += " AND e.created_at >= :start_date"
        if end_date:
            where_date_filter += " AND created_at <= :end_date"
            e_date_filter += " AND e.created_at <= :end_date"
        params = build_date_params(
            {"funnel_name": funnel_name, "funnel_id": funnel_id},
            start_date, end_date
        )
        rows = db.execute(text(f"""
            WITH user_journey AS (
                SELECT
                    user_id,
                    MAX(channel) AS channel,
                    MIN(created_at) AS first_seen,
                    MAX(created_at) AS last_seen,
                    COUNT(DISTINCT step_name) AS steps_completed,
                    BOOL_OR(event_type = 'complete') AS completed,
                    ROUND(EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) / 60, 1) AS total_minutes
                FROM events
                WHERE funnel_name = :funnel_name {where_date_filter}
                GROUP BY user_id
            ),
            user_last_step AS (
                SELECT DISTINCT ON (e.user_id)
                    e.user_id, fs.step_name AS last_step, fs.step_order
                FROM events e
                JOIN funnel_steps fs ON fs.step_name = e.step_name AND fs.funnel_id = :funnel_id
                WHERE e.funnel_name = :funnel_name {e_date_filter}
                ORDER BY e.user_id, fs.step_order DESC
            )
            SELECT
                uj.user_id, uj.channel, uj.first_seen, uj.last_seen,
                uj.steps_completed, uj.completed, uls.last_step, uj.total_minutes,
                CASE WHEN uj.completed THEN 'completed'
                     WHEN uj.steps_completed = 1 THEN 'dropped early'
                     ELSE 'dropped mid-funnel'
                END AS status
            FROM user_journey uj
            LEFT JOIN user_last_step uls ON uls.user_id = uj.user_id
            ORDER BY uj.first_seen DESC;
        """), params).mappings().all()
        users = [dict(r) for r in rows]
        if status:
            users = [u for u in users if u["status"] == status]
        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "total_users": len(users),
            "users": users
        }
    finally:
        db.close()