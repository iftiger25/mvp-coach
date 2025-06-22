from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import json

app = FastAPI()

class ConversationStage(str, Enum):
    WELCOME = "welcome"
    RISKIEST_ASSUMPTION = "riskiest_assumption"
    ASSUMPTION_VALIDATION = "assumption_validation"
    EXPERIMENT_DESIGN = "experiment_design"
    PROTOTYPING = "prototyping"
    SUCCESS_CRITERIA = "success_criteria"
    CONCLUSION = "conclusion"

class UserResponse(BaseModel):
    message: str
    current_stage: ConversationStage = ConversationStage.WELCOME
    conversation_history: list = []

# Coaching logic and prompts
coaching_flow = {
    ConversationStage.WELCOME: {
        "prompt": "Hey there! I'm your MVP Coach. Let's validate your AI product idea together. What's your AI product about?",
        "next_stage": ConversationStage.RISKIEST_ASSUMPTION
    },
    ConversationStage.RISKIEST_ASSUMPTION: {
        "prompt": "Great! What do you think is the riskiest assumption about your idea? (What's the most uncertain part that if proven wrong would make your idea fail?)",
        "next_stage": ConversationStage.ASSUMPTION_VALIDATION
    },
    ConversationStage.ASSUMPTION_VALIDATION: {
        "prompt": "Interesting. If this assumption turns out to be false, would your product still work? (yes/no)",
        "next_stage": ConversationStage.EXPERIMENT_DESIGN
    },
    ConversationStage.EXPERIMENT_DESIGN: {
        "prompt": "Let's test this assumption. What's the simplest way you could validate this? (Describe in 1-2 sentences)",
        "next_stage": ConversationStage.PROTOTYPING
    },
    ConversationStage.PROTOTYPING: {
        "prompt": "What tools or resources do you have available to build a quick prototype?",
        "next_stage": ConversationStage.SUCCESS_CRITERIA
    },
    ConversationStage.SUCCESS_CRITERIA: {
        "prompt": "What would success look like for this test? (What result would validate your assumption?)",
        "next_stage": ConversationStage.CONCLUSION
    },
    ConversationStage.CONCLUSION: {
        "prompt": "Awesome! Here's your action plan:\n1. Build the simple prototype you described\n2. Run your validation test\n3. Measure: {success_criteria}\nYou can do this in the next 24 hours! Want to save this plan? (yes/no)",
        "next_stage": None
    }
}

@app.get("/")
def read_root():
    return {"message": "AI MVP Coach API - POST to /coach/ to start"}

@app.post("/coach/")
async def coach(user_response: UserResponse):
    try:
        # Get current stage information
        current_stage_info = coaching_flow[user_response.current_stage]
        
        # Prepare response
        response = {
            "message": current_stage_info["prompt"],
            "next_stage": current_stage_info["next_stage"],
            "conversation_history": user_response.conversation_history + [
                {"user": user_response.message, "coach": current_stage_info["prompt"]}
            ]
        }
        
        # Special handling for conclusion stage
        if user_response.current_stage == ConversationStage.SUCCESS_CRITERIA:
            response["message"] = response["message"].format(
                success_criteria=user_response.message
            )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))