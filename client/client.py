#!/usr/bin/env python3
"""
Agent Fight Club - Reference Client
A simple CLI client for participating in combat challenges.
"""

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AGENT_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a fancy header"""
    print(f"\n{Colors.RED}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{'=' * 60}{Colors.END}\n")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ ERROR: {text}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

class AgentClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_assignment(self):
        """Fetch current combat assignment"""
        try:
            response = requests.get(
                f"{self.base_url}/agent/me",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to fetch assignment: {e}")
            return None
    
    def submit_answer(self, answer):
        """Submit answer to combat"""
        try:
            response = requests.post(
                f"{self.base_url}/agent/submit",
                headers=self.headers,
                json={"answer": answer}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to submit answer: {e}")
            if hasattr(e.response, 'json'):
                try:
                    error_detail = e.response.json().get('detail', str(e))
                    print_error(f"Server response: {error_detail}")
                except:
                    pass
            return None
    
    def get_result(self):
        """Get combat result"""
        try:
            response = requests.get(
                f"{self.base_url}/agent/result",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to fetch result: {e}")
            return None

def wait_for_combat(client):
    """Poll for combat to start"""
    print_header("AGENT FIGHT CLUB - CLIENT")
    print_info("Waiting for combat to start...")
    
    while True:
        assignment = client.get_assignment()
        if not assignment:
            time.sleep(2)
            continue
        
        state = assignment.get("state")
        
        if state == "RUNNING":
            return assignment
        elif state in ["COMPLETED", "EXPIRED"]:
            print_warning(f"Combat already {state.lower()}")
            return None
        
        print(f"{Colors.CYAN}Status: {state}{Colors.END}", end='\r')
        time.sleep(2)

def display_question(assignment):
    """Display the question"""
    prompt = assignment.get("prompt")
    choices = assignment.get("choices", [])
    deadline_ts = assignment.get("deadlineTs")
    
    print_header("COMBAT QUESTION")
    print(f"{Colors.BOLD}{prompt}{Colors.END}\n")
    
    # Display MCQ choices if available
    if choices:
        print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}")
        for i, choice in enumerate(choices):
            label = chr(65 + i)  # A, B, C, D...
            print(f"  {Colors.CYAN}{label}.{Colors.END} {choice}")
        print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}")
        print_info("Enter the letter (A, B, C, or D) of your answer")
    
    if deadline_ts:
        deadline = datetime.fromtimestamp(deadline_ts)
        remaining = (deadline - datetime.now()).total_seconds()
        print_warning(f"Time remaining: {int(remaining)} seconds")
        print_info(f"Deadline: {deadline.strftime('%H:%M:%S')}")
    
    return deadline_ts

def get_user_answer():
    """Get answer from user"""
    print(f"\n{Colors.BOLD}Enter your answer (press Ctrl+D or Ctrl+Z when done):{Colors.END}")
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}\n")
    answer = '\n'.join(lines).strip()
    
    if not answer:
        print_error("No answer provided")
        return None
    
    return answer

def submit_and_wait(client, answer):
    """Submit answer and wait for result"""
    print_info("Submitting answer...")
    
    result = client.submit_answer(answer)
    if not result:
        return False
    
    print_success("Answer submitted successfully!")
    
    print_info("Waiting for opponent and final results...")
    
    while True:
        time.sleep(2)
        result_data = client.get_result()
        
        if not result_data:
            continue
        
        state = result_data.get("state")
        if state in ["COMPLETED", "EXPIRED"]:
            return result_data
        
        print(f"{Colors.CYAN}Waiting for combat to complete...{Colors.END}", end='\r')

def display_results(result_data):
    """Display final results"""
    print_header("COMBAT RESULTS")
    
    state = result_data.get("state")
    my_status = result_data.get("myStatus")
    opponent_status = result_data.get("opponentStatus")
    my_answer = result_data.get("myAnswer")
    opponent_answer = result_data.get("opponentAnswer")
    
    print(f"{Colors.BOLD}Combat State:{Colors.END} {state}")
    print(f"{Colors.BOLD}Your Status:{Colors.END} {my_status}")
    print(f"{Colors.BOLD}Opponent Status:{Colors.END} {opponent_status}\n")
    
    if my_answer:
        print(f"{Colors.GREEN}{Colors.BOLD}YOUR ANSWER:{Colors.END}")
        print(f"{Colors.GREEN}{'─' * 60}")
        print(f"{my_answer}")
        print(f"{'─' * 60}{Colors.END}\n")
    else:
        print(f"{Colors.RED}You did not submit an answer (timeout){Colors.END}\n")
    
    if opponent_answer:
        print(f"{Colors.MAGENTA}{Colors.BOLD}OPPONENT'S ANSWER:{Colors.END}")
        print(f"{Colors.MAGENTA}{'─' * 60}")
        print(f"{opponent_answer}")
        print(f"{'─' * 60}{Colors.END}\n")
    else:
        print(f"{Colors.RED}Opponent did not submit an answer (timeout){Colors.END}\n")
    
    if my_status == "submitted" and opponent_status != "submitted":
        print_success("🏆 YOU WIN - Opponent timed out!")
    elif opponent_status == "submitted" and my_status != "submitted":
        print_error("💀 YOU LOSE - You timed out!")
    elif my_status == "submitted" and opponent_status == "submitted":
        print_info("⚔️ BOTH SUBMITTED - Review answers above")
    else:
        print_warning("⏱️ BOTH TIMED OUT - No winner")

def main():
    """Main client loop"""
    if not API_KEY:
        print_error("AGENT_KEY environment variable not set!")
        print_info("Usage: AGENT_KEY=your-api-key python client.py")
        print_info("Or create a .env file with: AGENT_KEY=your-api-key")
        sys.exit(1)
    
    client = AgentClient(API_KEY, API_BASE_URL)
    
    assignment = wait_for_combat(client)
    if not assignment:
        sys.exit(1)
    
    deadline_ts = display_question(assignment)
    
    answer = get_user_answer()
    if not answer:
        sys.exit(1)
    
    result_data = submit_and_wait(client, answer)
    if not result_data:
        sys.exit(1)
    
    display_results(result_data)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Client terminated by user{Colors.END}")
        sys.exit(0)
