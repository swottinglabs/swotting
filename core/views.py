from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, filters
from algoliasearch_django import raw_search
from .models import Platform, Tag, LearningResource
from .serializers import PlatformSerializer, TagSerializer, LearningResourceSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PlatformListCreateView(generics.ListCreateAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    http_method_names = ['get']

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']

class LearningResourceListCreateView(generics.ListCreateAPIView):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer
    http_method_names = ['get', 'post']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class LearningResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'put', 'delete']


def search_learning_resources(request):
    query = request.GET.get('q', '')
    params = {"hitsPerPage": 10}
    if query:
        response = raw_search(LearningResource, query, params)
        results = response.get('hits', [])
    else:
        results = []

    return JsonResponse(
        {
            'query': query, 
            'length': len(results),
            'results': results
        }, status=200)

def generate_learning_plan_with_llm(desired_skill: str, current_knowledge: str) -> dict:
    """
    Generate a structured learning plan using LangChain and GPT-4.
    """
    # Initialize the ChatOpenAI model
    chat_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv('OPENAI_API_KEY')
    )

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

    # Get response from LLM
    response = chat_model.invoke([HumanMessage(content=prompt)])
    
    try:
        # Parse the response content as JSON
        learning_plan = json.loads(response.content)
        return learning_plan
    except json.JSONDecodeError:
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

def search_courses_for_term(search_term: str, hits_per_page: int = 5) -> list:
    """
    Search for courses using a search term and return top matches.
    """
    params = {"hitsPerPage": hits_per_page}
    response = raw_search(LearningResource, search_term, params)
    return response.get('hits', [])

@api_view(['POST'])
def generate_curriculum(request):
    """
    Generate a personalized learning curriculum based on desired skills and current knowledge.
    """
    # Extract data from request
    desired_skill = request.data.get('desired_skill')
    current_knowledge = request.data.get('current_knowledge')

    # Validate input
    if not desired_skill or not current_knowledge:
        return Response(
            {'error': 'Both desired_skill and current_knowledge are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate learning plan using LLM
    learning_plan = generate_learning_plan_with_llm(desired_skill, current_knowledge)

    # Add course recommendations for each step
    for step in learning_plan.get('learningPlanSteps', []):
        search_term = step.get('search_term', '')
        recommended_courses = search_courses_for_term(search_term)
        step['recommended_courses'] = recommended_courses

    # Return the learning plan with course recommendations
    response_data = {
        'desired_skill': desired_skill,
        'current_knowledge': current_knowledge,
        'learning_plan': learning_plan
    }

    return Response(response_data, status=status.HTTP_200_OK)
