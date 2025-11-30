from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from classification.classify import *
from conversion.latex_conv import *
from s3_storage import S3Storage
from db_storage import MongoDBStorage
import google.generativeai as genai
import os
import base64
from PIL import Image
import io
from datetime import datetime
import re

app = FastAPI()

GENAI_API_KEY = "-Retracted-"
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

S3_BUCKET_NAME = "smart-clipboard-downloads"
AWS_ACCESS_KEY_ID = "-retracted-"
AWS_SECRET_ACCESS_KEY = "-retracted-"
AWS_REGION = "us-east-1"

s3_storage = None
if S3_BUCKET_NAME:
    s3_storage = S3Storage(
        bucket_name=S3_BUCKET_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

mongo_storage = MongoDBStorage()

class ClipboardData(BaseModel):
    text: str

class ScreenshotData(BaseModel):
    image: str
    type: str

class CalendarEventData(BaseModel):
    text: str
    description: str

@app.get("/")
async def welcome():
    return {"message": "Welcome to ClipSmart Classification API!"}

def process_text(text: str) -> str:
    """process text like SmartInterface.java"""
    return (text
        .replace("\\\\", "\\")
        .replace("\\n", "\n")
        .replace("\\\"", "\""))

def generate_ics(summary: str, start_date: str, end_date: str, description: str = "") -> str:
    """generate ICS for calendar event"""
    
    uid = f"clipmart-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    now = datetime.now().strftime('%Y%m%dT%H%M%SZ')
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//ClipSmart//Calendar Event//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now}
DTSTART:{start_date}
DTEND:{end_date}
SUMMARY:{summary}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR"""
    
    return ics_content

def format_date(date_text: str, api_key: str) -> dict:
    """extract date/time info with Gemini"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Extract date and time information from the following text and provide it in the exact JSON format below.
        If the text contains only a date without time, assume 9:00 AM for start time and 10:00 AM for end time.
        If end time is not specified, make it 1 hour after start time.
        
        Text: "{date_text}"
        
        Return ONLY valid JSON in this exact format:
        {{
            "start_date": "YYYYMMDDTHHMMSSZ",
            "end_date": "YYYYMMDDTHHMMSSZ", 
            "summary": "Brief event title (max 50 chars)",
            "has_valid_date": true/false
        }}
        
        Important:
        - Use UTC format (Z suffix)
        - If no valid date found, set has_valid_date to false
        - Summary should be a short, descriptive title for the event
        - Convert all times to 24-hour format
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        response_text = response_text.strip()
        
        import json
        result = json.loads(response_text)
        
        return result
        
    except Exception as e:
        print(f"Error formatting date with Gemini: {e}")
        return {
            "start_date": None,
            "end_date": None,
            "summary": "Event",
            "has_valid_date": False,
            "error": str(e)
        }

@app.post("/process")
async def process_clipboard(data: ClipboardData):
    print(f"Received clipboard text: {data.text}")
    
    processed_text = process_text(data.text)
    
    is_link = checkLink(data.text)
    is_date = checkDate(data.text)
    is_math = checkMath(data.text)
    is_address = checkAddress(data.text)
    
    classification = {"link": is_link, "date": is_date, "math" : is_math, "address" : is_address}
    
    actual_text = data.text
    
    latex_result = None
    s3_result = None
    if is_math and not is_link:
        print("\n" + "="*50)
        print("MATH CONTENT DETECTED!")
        print("="*50)
        print("Use Java application with --capture flag to take screenshot for LaTeX conversion")
        latex_result = "Math content detected - use Java screenshot capture"
        
        if s3_storage:
            output_data = {
                "message": "Math content detected - use Java screenshot capture",
                "text_length": len(processed_text),
                "preview": processed_text[:100] + "..." if len(processed_text) > 100 else processed_text,
                "classification": classification,
                "latex_conversion": latex_result
            }
            metadata = {
                "source": "text_input",
                "original_text": processed_text,
                "processing_type": "math_detection"
            }
            s3_result = s3_storage.upload_json_output(output_data, metadata)
            if s3_result["success"]:
                print(f"Math detection result stored to S3:")
                print(f"  JSON URL: {s3_result['url']}")
            else:
                print(f"S3 storage failed: {s3_result['error']}")
    
    response_data = {
        "message": "Welcome to ClipSmart! Text received successfully.",
        "text_length": len(processed_text),
        "preview": processed_text[:100] + "..." if len(processed_text) > 100 else processed_text,
        "classification": classification,
        "original_text": actual_text
    }
    
    if latex_result is not None:
        response_data["latex_conversion"] = latex_result
    
    if s3_result:
        response_data["s3_storage"] = {
            "url": s3_result["url"],
            "success": s3_result["success"],
            "content_type": s3_result.get("content_type", "application/json")
        }
    
    if mongo_storage.is_connected():
        mongo_storage.log_processing_request(
            endpoint="/process",
            content_data={"preview": processed_text[:100], "length": len(processed_text)},
            classification=classification,
            response_data=response_data
        )
    
    return response_data

@app.post("/process-image")
async def process_screenshot(data: ScreenshotData):
    print(f"Received screenshot data of type: {data.type}")
    
    try:
        image_bytes = base64.b64decode(data.image)
        image = Image.open(io.BytesIO(image_bytes))
        
        temp_path = "temp_screenshot.png"
        image.save(temp_path)
        
        if not GENAI_API_KEY:
            return {"error": "GENAI_API_KEY not configured"}
        
        print("Processing screenshot with AI...")
        latex_result = image_to_latex(temp_path, GENAI_API_KEY)
        
        processed_latex = process_text(latex_result) if latex_result else latex_result
        
        s3_result = None
        if s3_storage and processed_latex and not processed_latex.startswith("An error occurred"):
            is_math_result = checkMath(processed_latex) if processed_latex else False
            output_data = {
                "message": "Screenshot processed successfully",
                "latex_conversion": processed_latex,
                "is_math": is_math_result,
                "status": "success"
            }
            metadata = {
                "source": "screenshot",
                "type": data.type,
                "processing_timestamp": str(os.path.getmtime(temp_path)),
                "processing_type": "image_to_latex"
            }
            s3_result = s3_storage.upload_json_output(output_data, metadata)
            if s3_result["success"]:
                print(f"Screenshot processing result stored to S3:")
                print(f"  JSON URL: {s3_result['url']}")
            else:
                print(f"S3 storage failed: {s3_result['error']}")
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        is_math_result = checkMath(processed_latex) if processed_latex else False
        
        response = {
            "message": "Screenshot processed successfully",
            "latex_conversion": processed_latex,
            "is_math": is_math_result,
            "status": "success"
        }
        
        if s3_result:
            response["s3_storage"] = {
                "url": s3_result["url"],
                "success": s3_result["success"],
                "content_type": s3_result.get("content_type", "application/json")
            }
    
        if mongo_storage.is_connected():
            mongo_storage.log_processing_request(
                endpoint="/process-image",
                content_data={"preview": f"Screenshot ({data.type})", "length": len(data.image)},
                classification={"is_math": is_math_result},
                response_data=response
            )
        
        return response
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists("temp_screenshot.png"):
            os.remove("temp_screenshot.png")
        
        return {
            "error": f"Failed to process screenshot: {str(e)}",
            "status": "error"
        }

@app.post("/create-calendar-event")
async def create_calendar_event(data: CalendarEventData):
    """create calendar event from date text"""
    print(f"Received calendar event request for text: {data.text}")
    print(f"User description: {data.description}")
    
    if not GENAI_API_KEY:
        return {"error": "GENAI_API_KEY not configured", "status": "error"}
    
    try:
        date_info = format_date(data.text, GENAI_API_KEY)
        
        if not date_info.get("has_valid_date", False):
            return {
                "error": "Could not extract valid date from text",
                "status": "error",
                "original_text": data.text
            }
        
        ics_content = generate_ics(
            summary=date_info.get("summary", "Event"),
            start_date=date_info["start_date"],
            end_date=date_info["end_date"],
            description=data.description
        )
        
        s3_result = None
        if s3_storage:
            filename = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
            s3_result = s3_storage.upload_text_file(ics_content, filename, "text/calendar")
            
            if s3_result["success"]:
                print(f"ICS file stored to S3: {s3_result['url']}")
            else:
                print(f"S3 storage failed: {s3_result['error']}")
        
        response = {
            "message": "Calendar event created successfully",
            "status": "success",
            "ics_content": ics_content,
            "event_details": {
                "summary": date_info.get("summary", "Event"),
                "start_date": date_info["start_date"],
                "end_date": date_info["end_date"],
                "description": data.description
            },
            "original_text": data.text
        }
        
        if s3_result and s3_result["success"]:
            response["download_url"] = s3_result["url"]
            response["s3_storage"] = {
                "url": s3_result["url"],
                "success": s3_result["success"],
                "content_type": "text/calendar"
            }
        
        if mongo_storage.is_connected():
            mongo_storage.log_processing_request(
                endpoint="/create-calendar-event",
                content_data={"preview": data.text[:100], "length": len(data.text)},
                classification={"has_valid_date": date_info.get("has_valid_date", False)},
                response_data=response
            )
        
        return response
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return {
            "error": f"Failed to create calendar event: {str(e)}",
            "status": "error",
            "original_text": data.text
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
