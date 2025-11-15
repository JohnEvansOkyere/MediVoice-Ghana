import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.db.database import get_db
from app.db.models import User, Appointment
from app.models.schemas import AppointmentCreate, AppointmentResponse
from app.utils.auth import get_current_user
from app.config import settings

router = APIRouter()


@router.post("/book", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Book an appointment

    - Collects appointment details
    - Sends data to n8n webhook for processing
    - Stores appointment in database
    """

    try:
        # Create appointment record
        appointment = Appointment(
            user_id=current_user.id,
            full_name=appointment_data.full_name,
            phone=appointment_data.phone,
            preferred_date=appointment_data.preferred_date,
            preferred_time=appointment_data.preferred_time,
            reason=appointment_data.reason,
            status="pending"
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        # Send to n8n webhook
        try:
            async with httpx.AsyncClient() as client:
                n8n_payload = {
                    "appointment_id": appointment.id,
                    "user_email": current_user.email,
                    "full_name": appointment_data.full_name,
                    "phone": appointment_data.phone,
                    "preferred_date": appointment_data.preferred_date,
                    "preferred_time": appointment_data.preferred_time,
                    "reason": appointment_data.reason
                }

                response = await client.post(
                    settings.N8N_WEBHOOK_URL,
                    json=n8n_payload,
                    headers={"Authorization": f"Bearer {settings.N8N_API_KEY}"} if settings.N8N_API_KEY else {},
                    timeout=10.0
                )

                # Save n8n response
                appointment.n8n_response = response.json() if response.status_code == 200 else None
                db.commit()

                logger.info(f"Appointment sent to n8n: {appointment.id}")

        except Exception as e:
            logger.error(f"n8n webhook error: {str(e)}")
            # Continue even if n8n fails - appointment is saved

        return appointment

    except Exception as e:
        logger.error(f"Appointment booking error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to book appointment"
        )


@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's appointments"""

    appointments = db.query(Appointment).filter(
        Appointment.user_id == current_user.id
    ).order_by(Appointment.created_at.desc()).all()

    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific appointment"""

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment
