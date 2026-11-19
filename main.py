"""FastAPI backend using CPU-only Haar detection and compact LBP matching."""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models import (
    EnrollRequest, EnrollResponse, RecognizeRequest, RecognizeResponse,
    UserResponse, UsersListResponse, DeleteResponse, HealthResponse, FaceMatch
)
from face_detector import FaceDetector
from database import Database
from lbp_recognition import extract_lbp, compare_lbp

face_detector: Optional[FaceDetector] = None
database: Optional[Database] = None
# Conservative demo threshold. Real-world performance must be validated with consented test data.
LBP_DISTANCE_THRESHOLD = 0.42


@asynccontextmanager
async def lifespan(app: FastAPI):
    global face_detector, database
    print("Starting low-memory face recognition API...")
    face_detector = FaceDetector(min_detection_confidence=0.7)
    database = Database(db_path="data/helloface.db")
    print("Haar detector and LBP descriptor ready.")
    yield
    print("Shutting down face recognition API.")


app = FastAPI(
    title="PrivacyFace API",
    description="Consent-based, CPU-only face matching demo using OpenCV Haar + LBP.",
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://privacy-face-project.vercel.app",
        "https://privacy-face-project-git-main-aa-9848.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"]
)


@app.get("/")
async def root():
    return {"message": "PrivacyFace API", "version": "1.1.0", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    ready = face_detector is not None and database is not None
    return HealthResponse(
        status="healthy" if ready else "starting",
        models_loaded=ready,
        database_connected=database is not None,
        vector_store_ready=database is not None
    )


@app.post("/enroll", response_model=EnrollResponse)
async def enroll_user(request: EnrollRequest):
    if not request.consent:
        raise HTTPException(status_code=400, detail="Explicit consent is required before biometric enrollment.")
    try:
        existing = database.get_user_by_email(request.email)
        if existing:
            raise HTTPException(status_code=400, detail="This email is already enrolled.")
        faces = face_detector.detect_from_base64(request.image)
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected. Improve lighting and look at the camera.")
        if len(faces) > 1:
            raise HTTPException(status_code=400, detail="More than one face detected. Only one person should be in the frame.")
        face_crop, _bbox = faces[0]
        descriptor = extract_lbp(face_crop)
        user = database.create_user(
            name=request.name.strip(),
            email=request.email,
            embedding=descriptor
        )
        return EnrollResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            enrolled_at=user.enrolled_at,
            message=f"{user.name} enrolled successfully. The face descriptor is stored encrypted."
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(exc)}")


@app.post("/recognize", response_model=RecognizeResponse)
async def recognize_face(request: RecognizeRequest):
    try:
        faces = face_detector.detect_from_base64(request.image)
        if not faces:
            return RecognizeResponse(recognized=False, match=None, message="No face detected.")
        # Use the largest detected face for the demo.
        face_crop, bbox = max(faces, key=lambda item: item[1]["width"] * item[1]["height"])
        query_descriptor = extract_lbp(face_crop)

        best_user = None
        best_distance = float("inf")
        for user in database.get_all_users():
            if not user.embedding_encrypted:
                continue
            stored = database.decrypt_embedding(user.embedding_encrypted)
            distance = compare_lbp(query_descriptor, stored)
            if distance < best_distance:
                best_distance = distance
                best_user = user

        if best_user is None:
            return RecognizeResponse(recognized=False, match=None, message="No enrolled faces yet.")
        confidence = max(0.0, min(1.0, 1.0 - best_distance))
        if best_distance > LBP_DISTANCE_THRESHOLD:
            return RecognizeResponse(
                recognized=False, match=None,
                message=f"No confident match (similarity score: {confidence:.2f}). Try better lighting and a front-facing photo."
            )
        return RecognizeResponse(
            recognized=True,
            match=FaceMatch(
                user_id=best_user.id,
                name=best_user.name,
                email=best_user.email,
                confidence=confidence,
                bounding_box=bbox
            ),
            message=f"Possible match: {best_user.name} (LBP demo matcher)"
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recognition failed: {str(exc)}")


@app.get("/users", response_model=UsersListResponse)
async def get_users():
    try:
        users = database.get_all_users()
        return UsersListResponse(
            users=[
                UserResponse(user_id=u.id, name=u.name, email=u.email, enrolled_at=u.enrolled_at)
                for u in users
            ],
            total=len(users)
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(exc)}")


@app.delete("/users/{user_id}", response_model=DeleteResponse)
async def delete_user(user_id: int):
    try:
        user = database.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        database.delete_user(user_id)
        return DeleteResponse(message=f"Deleted {user.name}.", user_id=user_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(exc)}")


@app.get("/stats")
async def get_stats():
    try:
        return {
            "total_users": database.get_user_count(),
            "total_embeddings": database.get_user_count(),
            "recognition_method": "OpenCV Haar + spatial LBP",
            "distance_threshold": LBP_DISTANCE_THRESHOLD
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(exc)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
