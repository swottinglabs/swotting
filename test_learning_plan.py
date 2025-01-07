from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Load environment variables
load_dotenv()

def generate_learning_plan_with_openai(desired_skill: str, current_knowledge: str) -> dict:
    """
    Generate a structured learning plan using OpenAI's API directly.
    """
    # Debug: Check if API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Check your .env file.")
    print(f"API Key loaded: {'Yes' if api_key else 'No'}")
    print(f"API Key starts with: {api_key[:5]}...")
    
    print(f"\nGenerating learning plan for:")
    print(f"Desired Skill: {desired_skill}")
    print(f"Current Knowledge: {current_knowledge}")
    
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create the system prompt
        prompt = f"""You are a curriculum-generating assistant.
The user wants to learn: {desired_skill}.
The user's current knowledge is: {current_knowledge}.
Your task is to produce a learning plan with 3 to 8 steps that transitions the user from their current knowledge to the desired skill.
Each step should be concise and focus on a single skill or sub-topic.
Return the result in JSON with the following structure:

{{
  "learningPlanSteps": [
    {{
      "step_number": 1,
      "search_term": "term used to search for courses like this",
      "title": "Step Title",
      "description": "Short explanation of what this step entails"
    }},
    ...
  ]
}}"""

        print("\nSending request to OpenAI...")
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a curriculum-generating assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        try:
            # Parse the response content as JSON
            learning_plan = json.loads(response.choices[0].message.content)
            print("\nSuccessfully generated learning plan!")
            return learning_plan
        except json.JSONDecodeError as e:
            print(f"\nError parsing JSON: {e}")
            # If JSON parsing fails, return a structured error
            return {
                "learningPlanSteps": [
                    {
                        "step_number": 1,
                        "search_term": "basic " + desired_skill,
                        "title": "Getting Started",
                        "description": "Introduction to " + desired_skill
                    }
                ]
            }
    except Exception as e:
        print(f"Error using OpenAI API: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        raise

def test_learning_plan_generation():
    # Test case 1: Learning Python
    print("\n=== Test Case 1: Learning Python ===")
    plan1 = generate_learning_plan_with_openai(
        "Python Programming",
        "I know basic HTML and CSS, but no programming languages"
    )
    print(json.dumps(plan1, indent=2))

if __name__ == "__main__":
    test_learning_plan_generation() 