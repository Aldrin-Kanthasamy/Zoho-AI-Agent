import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from .database import engine, get_db, Base
from . import models

load_dotenv()

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Zoho Sprint/Desk Integration")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-2.1")

scheduler = BackgroundScheduler()


def choose_assignee(db: Session, skill: str):
    skill_lower = skill.strip().lower()
    candidate = (
        db.query(models.User)
        .filter(models.User.is_available == True)
        .order_by(models.User.id)
        .all()
    )
    best = None
    best_load = 999
    for user in candidate:
        if not user.skills:
            continue
        skill_set = [s.strip().lower() for s in user.skills.split(",") if s.strip()]
        if skill_lower in skill_set:
            task_count = db.query(models.Task).filter(models.Task.assignee_id == user.id, models.Task.status != models.TaskStatus.completed).count()
            ticket_count = db.query(models.Ticket).filter(models.Ticket.assignee_id == user.id, models.Ticket.status != models.TicketStatus.resolved).count()
            load = task_count + ticket_count
            if load < best_load:
                best_load = load
                best = user
    return best


def generate_daily_standup(db: Session):
    pending_tasks = db.query(models.Task).filter(models.Task.status != models.TaskStatus.completed).all()
    pending_tickets = db.query(models.Ticket).filter(models.Ticket.status != models.TicketStatus.resolved).all()
    body = "Daily Standup Summary\n\nTasks:\n"
    for t in pending_tasks:
        body += f"- {t.title} (priority {t.priority}, status {t.status}, assigned to {t.assignee.name if t.assignee else 'unassigned'})\n"
    body += "\nTickets:\n"
    for t in pending_tickets:
        body += f"- {t.subject} (priority {t.priority}, status {t.status}, assigned to {t.assignee.name if t.assignee else 'unassigned'})\n"
    print("[Standup]", body)


@scheduler.scheduled_job("cron", hour=9)
def daily_standup_job():
    db = next(get_db())
    generate_daily_standup(db)

scheduler.start()


@app.get("/health")
def health_check():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/webhook/zohosprint")
async def zohosprint_webhook(payload: dict, db: Session = Depends(get_db)):
    # payload should include fields: external_id, title, description, skill_needed, priority
    external_id = payload.get("external_id")
    title = payload.get("title")
    description = payload.get("description")
    skill_needed = payload.get("skill_needed")
    priority = payload.get("priority", "Medium")

    if not title or not skill_needed:
        raise HTTPException(status_code=400, detail="title and skill_needed are required")

    task = models.Task(
        external_id=external_id,
        title=title,
        description=description,
        skill_needed=skill_needed,
        priority=priority,
        status=models.TaskStatus.open,
    )

    assignee = choose_assignee(db, skill_needed)
    if assignee:
        task.assignee = assignee

    db.add(task)
    db.commit()
    db.refresh(task)

    return {"task_id": task.id, "assigned_to": assignee.name if assignee else None}


@app.post("/webhook/zohodesk")
async def zohodesk_webhook(payload: dict, db: Session = Depends(get_db)):
    external_id = payload.get("external_id")
    subject = payload.get("subject")
    description = payload.get("description")
    skill_needed = payload.get("skill_needed")
    priority = payload.get("priority", "Medium")

    if not subject or not skill_needed:
        raise HTTPException(status_code=400, detail="subject and skill_needed are required")

    ticket = models.Ticket(
        external_id=external_id,
        subject=subject,
        description=description,
        skill_needed=skill_needed,
        priority=priority,
        status=models.TicketStatus.open,
    )

    assignee = choose_assignee(db, skill_needed)
    if assignee:
        ticket.assignee = assignee

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {"ticket_id": ticket.id, "assigned_to": assignee.name if assignee else None}


@app.get("/superadmin/dashboard")
def superadmin_dashboard(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    tasks = db.query(models.Task).all()
    tickets = db.query(models.Ticket).all()
    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "skills": u.skills,
                "role": u.role,
                "is_available": u.is_available,
            }
            for u in users
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "assignee": t.assignee.name if t.assignee else None,
            }
            for t in tasks
        ],
        "tickets": [
            {
                "id": x.id,
                "subject": x.subject,
                "status": x.status,
                "assignee": x.assignee.name if x.assignee else None,
            }
            for x in tickets
        ],
    }


@app.post("/admin/query")
async def admin_nl_command(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    natural_language = body.get("text")
    if not natural_language:
        raise HTTPException(status_code=400, detail="text is required")

    # Placeholder: integrate with Anthropic for actual natural language task control.
    # For now, we parse simple commands.
    if "assign" in natural_language.lower():
        # command format: assign task <id> to <user_id>
        parts = natural_language.lower().split()
        try:
            if "task" in parts:
                task_index = parts.index("task") + 1
                task_id = int(parts[task_index])
                if "to" in parts:
                    to_index = parts.index("to") + 1
                    user_id = int(parts[to_index])
                    task = db.query(models.Task).get(task_id)
                    user = db.query(models.User).get(user_id)
                    if not task or not user:
                        raise ValueError
                    task.assignee = user
                    db.commit()
                    return {"message": f"Task {task_id} assigned to {user.name}"}
        except Exception:
            pass

    return {"message": "NL command received", "input": natural_language}
