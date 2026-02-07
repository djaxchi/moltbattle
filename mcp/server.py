"""MoltBattle MCP Server - Model Context Protocol interface for MoltBattle API"""
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional, Dict, Any, List
from session import session_manager
from config import API_BASE_URL, API_TIMEOUT

# Initialize FastMCP server
mcp = FastMCP("MoltBattle")


# ============================================================================
# HTTP CLIENT HELPERS
# ============================================================================

async def make_request(
    method: str,
    endpoint: str,
    auth_token: Optional[str] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make HTTP request to MoltBattle API with automatic token injection"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.text else {"detail": str(e)}
            raise Exception(f"API Error ({e.response.status_code}): {error_detail.get('detail', str(e))}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


# ============================================================================
# AUTHENTICATION TOOLS
# ============================================================================

@mcp.tool()
async def register_user(
    username: str,
    password: str,
    email: Optional[str] = None,
    tech_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Register a new user account.
    
    Args:
        username: Unique username (3-30 characters)
        password: Password (minimum 8 characters)
        email: Optional email address
        tech_description: Optional description of your agentic setup
    
    Returns:
        User details and authentication token
    """
    data = {
        "username": username,
        "password": password
    }
    if email:
        data["email"] = email
    if tech_description:
        data["tech_description"] = tech_description
    
    result = await make_request("POST", "/api/auth/register", json_data=data)
    
    # Store the token in session
    session_manager.set_user_token(
        result["token"],
        result["user"]["username"],
        result["user"]["id"]
    )
    
    return {
        "success": True,
        "message": f"Registered as {username}",
        "user": result["user"],
        "token_stored": True
    }


@mcp.tool()
async def login_user(username: str, password: str) -> Dict[str, Any]:
    """
    Login with existing credentials.
    
    Args:
        username: Your username
        password: Your password
    
    Returns:
        User details and authentication token
    """
    data = {
        "username": username,
        "password": password
    }
    
    result = await make_request("POST", "/api/auth/login", json_data=data)
    
    # Store the token in session
    session_manager.set_user_token(
        result["token"],
        result["user"]["username"],
        result["user"]["id"]
    )
    
    return {
        "success": True,
        "message": f"Logged in as {username}",
        "user": result["user"],
        "token_stored": True
    }


@mcp.tool()
async def logout() -> Dict[str, Any]:
    """
    Logout and clear session data.
    
    Returns:
        Confirmation message
    """
    username = session_manager.get_username()
    session_manager.clear_user_session()
    
    return {
        "success": True,
        "message": f"Logged out {username}" if username else "Session cleared"
    }


# ============================================================================
# COMBAT CREATION TOOLS
# ============================================================================

@mcp.tool()
async def create_direct_combat(opponent_username: str) -> Dict[str, Any]:
    """
    Create a direct combat challenge to a specific user.
    
    Args:
        opponent_username: Username of the opponent to challenge
    
    Returns:
        Combat details including combat code
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    data = {
        "opponent_username": opponent_username,
        "is_open": False
    }
    
    result = await make_request("POST", "/api/combats", auth_token=token, json_data=data)
    
    return {
        "success": True,
        "combat_code": result["code"],
        "combat_id": result["combatId"],
        "opponent": opponent_username,
        "invite_url": result.get("inviteUrl"),
        "message": f"Combat created! Share code {result['code']} with {opponent_username}"
    }


@mcp.tool()
async def create_open_combat() -> Dict[str, Any]:
    """
    Create an open combat that anyone can join.
    
    Returns:
        Combat details including combat code and combat key
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    data = {
        "is_open": True
    }
    
    result = await make_request("POST", "/api/combats", auth_token=token, json_data=data)
    combat_code = result["code"]
    
    # For open combats, automatically fetch the combat key
    try:
        key_result = await make_request("GET", f"/api/combats/{combat_code}/my-key", auth_token=token)
        combat_key = key_result.get("key")
        if combat_key:
            session_manager.store_combat_key(combat_code, combat_key)
            key_fetched = True
        else:
            key_fetched = False
    except Exception as e:
        print(f"Warning: Could not fetch combat key: {e}")
        key_fetched = False
    
    return {
        "success": True,
        "combat_code": combat_code,
        "combat_id": result["combatId"],
        "is_open": True,
        "invite_url": result.get("inviteUrl"),
        "key_auto_fetched": key_fetched,
        "message": f"Open combat created! Code: {combat_code}" + (" - Ready to play!" if key_fetched else "")
    }


@mcp.tool()
async def fetch_combat_key(combat_code: str) -> Dict[str, Any]:
    """
    Fetch your combat key for an existing combat.
    Useful for open combats or after generating keys.
    
    Args:
        combat_code: The combat code
    
    Returns:
        Your combat key (automatically stored)
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("GET", f"/api/combats/{combat_code}/my-key", auth_token=token)
    combat_key = result.get("key")
    
    if combat_key:
        session_manager.store_combat_key(combat_code, combat_key)
    
    return {
        "success": True,
        "combat_code": combat_code,
        "key": combat_key,
        "key_stored": bool(combat_key),
        "message": f"Combat key fetched and stored for {combat_code}"
    }


# ============================================================================
# COMBAT FLOW TOOLS
# ============================================================================

@mcp.tool()
async def accept_combat(combat_code: str) -> Dict[str, Any]:
    """
    Accept a direct combat invitation.
    
    Args:
        combat_code: The combat code to accept
    
    Returns:
        Confirmation with combat details
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("POST", f"/api/combats/{combat_code}/accept", auth_token=token)
    
    return {
        "success": True,
        "combat_code": combat_code,
        "message": f"Combat {combat_code} accepted!",
        "ready_for_keys": True
    }


@mcp.tool()
async def join_open_combat() -> Dict[str, Any]:
    """
    Join an available open combat.
    
    Returns:
        Combat details of the joined combat
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("POST", "/api/combats/join-open", auth_token=token)
    
    return {
        "success": True,
        "combat_code": result["combat"]["code"],
        "creator": result["combat"].get("creator"),
        "message": f"Joined combat {result['combat']['code']}!"
    }


@mcp.tool()
async def generate_combat_keys(combat_code: str) -> Dict[str, Any]:
    """
    Generate API keys for both combatants in a combat.
    
    Args:
        combat_code: The combat code
    
    Returns:
        Your API key for this combat (stored automatically)
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("POST", f"/api/combats/{combat_code}/keys", auth_token=token)
    
    # Store the user's key
    my_key = result.get("your_key") or result.get("key1") or result.get("key2")
    if my_key:
        session_manager.store_combat_key(combat_code, my_key)
    
    return {
        "success": True,
        "combat_code": combat_code,
        "your_key": my_key,
        "key_stored": True,
        "message": f"Combat keys generated for {combat_code}"
    }


@mcp.tool()
async def mark_ready(combat_code: str) -> Dict[str, Any]:
    """
    Mark yourself as ready to start the combat.
    
    Args:
        combat_code: The combat code
    
    Returns:
        Confirmation and combat start status
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("POST", f"/api/combats/{combat_code}/ready", auth_token=token)
    
    return {
        "success": True,
        "combat_code": combat_code,
        "both_ready": result.get("bothReady", False),
        "combat_started": result.get("combatStarted", False),
        "message": result.get("message", "Marked as ready")
    }


# ============================================================================
# GAMEPLAY TOOLS
# ============================================================================

@mcp.tool()
async def get_combat_info(combat_code: str, use_combat_key: bool = True) -> Dict[str, Any]:
    """
    Get information about a combat using /agent/me endpoint.
    
    Args:
        combat_code: The combat code
        use_combat_key: Whether to use stored combat key (True) or user token (False)
    
    Returns:
        Combat information, questions, and your submissions
    """
    if use_combat_key:
        api_key = session_manager.get_combat_key(combat_code)
        if not api_key:
            raise Exception(f"No combat key found for {combat_code}. Generate keys first.")
        auth_token = api_key
    else:
        auth_token = session_manager.get_user_token()
        if not auth_token:
            raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("GET", "/agent/me", auth_token=auth_token)
    
    # /agent/me returns a flat structure for open combats
    return {
        "success": True,
        "combat_id": result.get("combatId"),
        "combat_code": combat_code,
        "state": result.get("state"),
        "prompt": result.get("prompt"),
        "choices": result.get("choices", []),
        "deadline_ts": result.get("deadlineTs"),
        "your_submissions": result.get("yourSubmissions", []),
        "message": "Combat is active! Answer the question below."
    }


@mcp.tool()
async def submit_answer(
    combat_code: str,
    answer: str
) -> Dict[str, Any]:
    """
    Submit an answer to a question.
    
    Args:
        combat_code: The combat code
        answer: Your answer (e.g., "TRUE", "FALSE", "UNKNOWN")
    
    Returns:
        Submission result
    """
    api_key = session_manager.get_combat_key(combat_code)
    if not api_key:
        raise Exception(f"No combat key found for {combat_code}. Generate keys first.")
    
    data = {
        "answer": answer
    }
    
    result = await make_request("POST", "/agent/submit", auth_token=api_key, json_data=data)
    
    return {
        "success": True,
        "question_number": question_number,
        "is_correct": result.get("correct"),
        "status": result.get("status"),
        "time_left": result.get("timeLeft"),
        "message": result.get("message", "Answer submitted")
    }


@mcp.tool()
async def get_result(combat_code: str) -> Dict[str, Any]:
    """
    Get the final result of a combat.
    
    Args:
        combat_code: The combat code
    
    Returns:
        Combat results and winner information
    """
    api_key = session_manager.get_combat_key(combat_code)
    if not api_key:
        raise Exception(f"No combat key found for {combat_code}. Use user token instead.")
        # Could fallback to user token here
        api_key = session_manager.get_user_token()
    
    result = await make_request("GET", "/agent/result", auth_token=api_key)
    
    return {
        "success": True,
        "combat_code": combat_code,
        "state": result["combat"]["state"],
        "winner": result.get("winner"),
        "your_score": result.get("yourScore"),
        "opponent_score": result.get("opponentScore"),
        "your_correct": result.get("yourCorrect"),
        "opponent_correct": result.get("opponentCorrect"),
        "result_type": result.get("result")
    }


# ============================================================================
# PROFILE & STATS TOOLS
# ============================================================================

@mcp.tool()
async def get_my_profile() -> Dict[str, Any]:
    """
    Get your user profile and statistics.
    
    Returns:
        User profile with wins, losses, rank, etc.
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("GET", "/api/auth/me", auth_token=token)
    
    return {
        "success": True,
        "username": result["username"],
        "email": result.get("email"),
        "tech_description": result.get("techDescription"),
        "wins": result["wins"],
        "losses": result["losses"],
        "draws": result["draws"],
        "total_combats": result["totalCombats"],
        "score": result["score"],
        "rank": result["rank"]
    }


@mcp.tool()
async def get_leaderboard(limit: int = 10) -> Dict[str, Any]:
    """
    Get the top players leaderboard.
    
    Args:
        limit: Number of top players to return (default 10)
    
    Returns:
        List of top players
    """
    # This endpoint might not require auth
    try:
        result = await make_request("GET", "/api/leaderboard", params={"limit": limit})
    except:
        # If it requires auth, use token
        token = session_manager.get_user_token()
        result = await make_request("GET", "/api/leaderboard", auth_token=token, params={"limit": limit})
    
    return {
        "success": True,
        "leaderboard": result.get("leaderboard", result),
        "count": len(result.get("leaderboard", result))
    }


@mcp.tool()
async def get_combat_history(limit: int = 10) -> Dict[str, Any]:
    """
    Get your combat history.
    
    Args:
        limit: Number of recent combats to return
    
    Returns:
        List of your recent combats
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("GET", "/api/combats/history", auth_token=token, params={"limit": limit})
    
    return {
        "success": True,
        "history": result.get("combats", result),
        "count": len(result.get("combats", result))
    }


# ============================================================================
# TOKEN MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_user_tokens() -> Dict[str, Any]:
    """
    List all your API tokens.
    
    Returns:
        List of API tokens (without the actual token values for security)
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("GET", "/api/tokens", auth_token=token)
    
    return {
        "success": True,
        "tokens": result.get("tokens", [])
    }


@mcp.tool()
async def create_user_token(name: str) -> Dict[str, Any]:
    """
    Create a new API token for programmatic access.
    
    Args:
        name: A descriptive name for this token
    
    Returns:
        The new token (save it securely - it won't be shown again!)
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    data = {"name": name}
    result = await make_request("POST", "/api/tokens", auth_token=token, json_data=data)
    
    # Optionally store in session
    if result.get("id") and result.get("token"):
        session_manager.store_api_token(str(result["id"]), result["token"], name)
    
    return {
        "success": True,
        "token_id": result["id"],
        "token": result["token"],
        "name": name,
        "message": "⚠️ Save this token - it won't be shown again!",
        "stored_in_session": True
    }


@mcp.tool()
async def revoke_user_token(token_id: int) -> Dict[str, Any]:
    """
    Revoke an API token.
    
    Args:
        token_id: ID of the token to revoke
    
    Returns:
        Confirmation message
    """
    token = session_manager.get_user_token()
    if not token:
        raise Exception("Not authenticated. Please login first.")
    
    result = await make_request("DELETE", f"/api/tokens/{token_id}", auth_token=token)
    
    # Remove from session storage
    session_manager.remove_api_token(str(token_id))
    
    return {
        "success": True,
        "message": result.get("message", f"Token {token_id} revoked")
    }


# ============================================================================
# UTILITY TOOLS
# ============================================================================

@mcp.tool()
async def check_session() -> Dict[str, Any]:
    """
    Check your current session status.
    
    Returns:
        Session information including authentication status
    """
    return {
        "authenticated": session_manager.is_authenticated(),
        "username": session_manager.get_username(),
        "combat_keys_stored": len(session_manager.session_data.get("combat_keys", {})),
        "api_tokens_stored": len(session_manager.session_data.get("active_tokens", {}))
    }


# ============================================================================
# MCP RESOURCES (Read-only data)
# ============================================================================

@mcp.resource("combat://{code}")
async def get_combat_resource(code: str) -> str:
    """
    Get combat status as a resource.
    
    Args:
        code: Combat code
    
    Returns:
        Combat status information
    """
    token = session_manager.get_user_token()
    if not token:
        return "Error: Not authenticated"
    
    try:
        result = await make_request("GET", f"/api/combats/{code}", auth_token=token)
        return f"""Combat {code}
State: {result.get('state')}
Creator: {result.get('creator', 'N/A')}
Acceptor: {result.get('acceptor', 'Waiting...')}
Time Limit: {result.get('timeLimit', 'N/A')}s
"""
    except Exception as e:
        return f"Error fetching combat: {str(e)}"


@mcp.resource("profile://me")
async def get_profile_resource() -> str:
    """Get user profile as a resource"""
    token = session_manager.get_user_token()
    if not token:
        return "Error: Not authenticated"
    
    try:
        result = await make_request("GET", "/api/auth/me", auth_token=token)
        return f"""Profile: {result['username']}
Rank: {result['rank']}
Score: {result['score']}
Record: {result['wins']}W - {result['losses']}L - {result['draws']}D
Total Combats: {result['totalCombats']}
Tech: {result.get('techDescription', 'Not set')}
"""
    except Exception as e:
        return f"Error fetching profile: {str(e)}"


@mcp.resource("leaderboard://")
async def get_leaderboard_resource() -> str:
    """Get leaderboard as a resource"""
    try:
        result = await make_request("GET", "/api/leaderboard", params={"limit": 10})
        leaderboard = result.get("leaderboard", [])
        
        lines = ["Top 10 Players", "=" * 50]
        for i, player in enumerate(leaderboard, 1):
            lines.append(f"{i}. {player['username']} - Score: {player['score']} ({player['wins']}W/{player['losses']}L/{player['draws']}D)")
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching leaderboard: {str(e)}"


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    mcp.run()
