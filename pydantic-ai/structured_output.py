from pydantic import BaseModel
from pydantic_ai import Agent
import os
from dotenv import load_dotenv
class Response(BaseModel):
    rating: float

agent = Agent(
    'google-gla:gemini-1.5-flash',
    system_prompt='Given a movie review, rate it from 1 to 10.',
    result_type=Response
)


result = agent.run_sync('The movie is super slow and boring.')
print(result.data)

# Example 2 with int rating
from pydantic import BaseModel

class Response(BaseModel):
    rating: int


agent = Agent(
    'google-gla:gemini-1.5-flash',
    system_prompt='Given a movie review, rate it from 1 to 10.',
    result_type=Response
)

result = agent.run_sync('The movie is super slow and boring.')
print(result.data)
