import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api"

async def run_tests():
    async with httpx.AsyncClient() as client:
        print("1. Testing /api/health")
        resp = await client.get(f"{BASE_URL}/health")
        print(f"Health: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200

        print("\n2. Testing POST /api/start")
        start_payload = {
            "student_id": "TEST-101",
            "session_id": "test-sess-uuid-001"
        }
        resp = await client.post(f"{BASE_URL}/start", json=start_payload)
        print(f"Start: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200
        start_data = resp.json()

        print("\n3. Testing POST /api/answer (Trial 1)")
        answer_payload = {
            "session_id": start_data["session_id"],
            "student_id": "TEST-101",
            "item_id": 1,
            "task_id": "ASAT-Sustained",
            "stimulus": "circle",
            "response": "Space",
            "correct": True,
            "reaction_time_ms": 350,
            "difficulty_level": 1
        }
        resp = await client.post(f"{BASE_URL}/answer", json=answer_payload)
        print(f"Answer: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200

        print("\n4. Testing POST /api/finish")
        finish_payload = {
            "session_id": start_data["session_id"],
            "student_id": "TEST-101",
            "scores": {
                "sustained": 92.5,
                "selective": 88.0,
                "divided": 75.0,
                "executive": 82.5,
                "overall": 84.5,
                "percentile": 85
            },
            "module_results": {
                "sustained": {
                    "rtVariabilityScore": 0.12,
                    "fatigueScore": -0.05
                }
            }
        }
        resp = await client.post(f"{BASE_URL}/finish", json=finish_payload)
        print(f"Finish: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200

        print("\n5. Testing GET /api/result/{session_id}")
        resp = await client.get(f"{BASE_URL}/result/{start_data['session_id']}")
        print(f"Result: {resp.status_code} - {json.dumps(resp.json(), indent=2)}")
        assert resp.status_code == 200
        
        print("\nAll MentiScope API endpoints verified successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
