import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api"

async def run_tests():
    # Use an httpx Client to maintain session cookies
    async with httpx.AsyncClient() as client:
        print("--- Testing Legacy Frontend API Endpoints ---")
        
        print("\n1. POST /api/auth/register (Faculty)")
        payload = {
            "fullName": "Test Faculty",
            "email": "faculty@test.com",
            "username": "faculty_user",
            "password": "password123"
        }
        resp = await client.post(f"{BASE_URL}/auth/register", json=payload)
        print(f"Register: {resp.status_code} - {resp.text}")
        if resp.status_code == 409: # Already exists from previous run
            print("Faculty already registered, proceeding to login.")
        else:
            assert resp.status_code == 201
            
        print("\n2. POST /api/auth/login (Faculty)")
        payload = {
            "username": "faculty_user",
            "password": "password123"
        }
        resp = await client.post(f"{BASE_URL}/auth/login", json=payload)
        print(f"Login: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200
        
        print("\n3. POST /api/students (Register Student)")
        payload = {
            "fullName": "Test Student Legacy",
            "studentId": "LEGACY-101",
            "age": 12,
            "grade": "6th",
            "school": "Test Academy"
        }
        resp = await client.post(f"{BASE_URL}/students", json=payload)
        print(f"Student: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200 or resp.status_code == 201
        student_data = resp.json()
        student_id = student_data.get("studentId")
        
        print("\n4. POST /api/sessions (Create Session)")
        payload = {
            "studentId": student_id
        }
        resp = await client.post(f"{BASE_URL}/sessions", json=payload)
        print(f"Session: {resp.status_code} - {resp.text}")
        assert resp.status_code == 201
        session_data = resp.json()
        session_id = session_data.get("sessionId")
        
        print("\n5. POST /api/sessions/{id}/events (Log Events)")
        payload = {
            "studentId": student_id,
            "events": [
                {
                    "construct": "Attention",
                    "taskId": "ASAT",
                    "itemId": 1,
                    "stimulus": "circle",
                    "eventType": "TRIAL",
                    "response": "Space",
                    "correct": True,
                    "reactionTimeMs": 400,
                    "errorType": "",
                    "difficultyLevel": 1
                }
            ]
        }
        resp = await client.post(f"{BASE_URL}/sessions/{session_id}/events", json=payload)
        print(f"Events: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200
        
        print("\n6. PATCH /api/sessions/{id} (Finish Assessment)")
        payload = {
            "studentId": student_id,
            "scores": {
                "sustained": 90.0,
                "selective": 85.0,
                "divided": 80.0,
                "executive": 88.0,
                "overall": 85.75,
                "percentile": 82
            },
            "moduleResults": {
                "sustained": {"rtVariabilityScore": 0.1}
            }
        }
        resp = await client.patch(f"{BASE_URL}/sessions/{session_id}", json=payload)
        print(f"Finish: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200
        
        print("\n7. GET /api/students (Faculty Dashboard)")
        resp = await client.get(f"{BASE_URL}/students")
        print(f"Dashboard: {resp.status_code} - {json.dumps(resp.json(), indent=2)}")
        assert resp.status_code == 200
        
        print("\nAll Legacy Frontend API endpoints verified successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
