from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from model_loader import predict_text
from alert_engine import send_alert_if_needed
from database import get_db
from models import Incident
from schemas import ClassifyRequest, ClassifyResponse, IncidentOut, IncidentUpdate
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest, db: Session = Depends(get_db)):
    result = predict_text(request.text)

    incident = Incident(
        text       = request.text,
        platform   = request.platform,
        user_id    = request.user_id,
        context_id = request.context_id,
        label      = result["label"],
        severity   = result["severity"],
        confidence = result["confidence"],
        timestamp  = datetime.utcnow()
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    alert_sent = send_alert_if_needed(
        result["severity"], request.text,
        request.platform, incident.id
    )

    return ClassifyResponse(
        text       = request.text,
        label      = result["label"],
        severity   = result["severity"],
        confidence = result["confidence"],
        scores     = result["scores"],
        alert_sent = alert_sent
    )

@router.get("/incidents", response_model=List[IncidentOut])
def get_incidents(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Incident).order_by(
        Incident.timestamp.desc()
    ).limit(limit).all()

@router.get("/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    return db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

@router.patch("/incidents/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, update: IncidentUpdate,
                    db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    if update.reviewed is not None:
        incident.reviewed = update.reviewed
    db.commit()
    db.refresh(incident)
    return incident