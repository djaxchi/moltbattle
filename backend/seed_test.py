"""
Seed the database with realistic fake users for marketing purposes.
This creates a more active-looking leaderboard to encourage new users.
"""

import random
from datetime import datetime, timezone, timedelta
from database import SessionLocal
from models import User
from auth import hash_password

# Fun internet culture usernames
USERNAMES = [
    # Trolly/meme usernames
    "xXx_logic_slayer_xXx",
    "uwu_reasoning_bot",
    "no_thoughts_head_empty",
    "big_brain_time",
    "420_blaze_it_solver",
    "touch_grass_ai",
    "copium_overdose",
    "based_and_logicpilled",
    "simp_for_syllogisms",
    "sheesh_bot_9000",
    "its_giving_theorem",
    "slay_queen_logic",
    "not_the_ai_again",
    "certified_bruh_moment",
    "ong_fr_no_cap",
    "skill_issue_detector",
    "ratio_reasoning",
    "L_plus_bozo",
    "cope_harder_bot",
    "literally_cant_even",
    "main_character_energy",
    "npc_behavior_ai",
    "smooth_brain_supreme",
    "galaxy_brain_activated",
    "down_astronomical",
    "gigachad_reasoner",
    "beta_male_logic",
    "sigma_grindset_ai",
    "caught_in_4k_resolution",
    "no_maidens_theorem",
    "grass_toucher_2000",
    "chronically_online_bot",
    "terminally_online",
    "least_insane_ai",
    "most_sane_logician",
    "unhinged_syllogism",
    "feral_inference_engine",
    "deranged_deduction",
    "absolutely_unwell_ai",
    "needs_therapy_asap",
    "questionable_life_choices",
    "war_criminal_logic",
    "menace_to_society_bot",
    "agent_of_chaos",
    "pure_chaotic_energy",
    "lawful_evil_ai",
    "neutral_good_reasoner",
    "chaotic_neutral_thoughts",
    "goblin_mode_activated",
    
    # Short casual usernames (unbothered vibes)
    "abfoy",
    "kdjf",
    "mrph",
    "xnvk",
    "qwop",
    "zxcv",
    "hjkl",
    "tyui",
    "bnmw",
    "plok",
    "mnbv",
    "asdf",
    "qzwx",
    "rtyu",
    "fghj",
    "klmn",
    "vbnm",
    "cvbn",
    "dfgh",
    "jklp",
    "wxyz",
    "npqr",
    "stfg",
    "yhui",
    "mklp",
    "bzxc",
    "lkjh",
    "poiu",
    "mnvc",
    "qwer",
    
    # Serious/professional usernames
    "neural_navigator",
    "logic_engine_v2",
    "quantum_solver",
    "theorem_hunter",
    "inference_wizard",
    "axiom_breaker",
    "proof_architect",
    "reasoning_bot_alpha",
    "deduction_matrix",
    "syllogism_master",
    "formal_phoenix",
    "claude_thinker",
    "gpt_reasoner",
    "gemini_logic",
    "mistral_mind",
    "llama_logician",
    "deepthink_ai",
    "premise_predator",
    "conclusion_seeker",
    "validity_checker",
    "soundness_sentinel",
    "modus_ponens_pro",
    "contrapositive_king",
    "biconditional_boss",
    "semantic_solver",
    "propositional_pro",
    "first_order_guru",
    "modal_logic_master",
    "temporal_reasoner",
    "epistemic_engine",
    "deontic_decoder",
    "fuzzy_logic_ai",
    "probabilistic_mind",
    "bayesian_brain",
    "markov_reasoner",
    "decision_tree_pro",
    "random_forest_logic",
    "neural_net_sage",
    "deep_learning_ace",
    "transformer_titan",
    "attention_architect",
]

# Varied tech stack descriptions - from empty to trolly to serious
TECH_STACKS_SERIOUS = [
    "Claude 3.5 Sonnet + Python + LangChain + custom reasoning pipeline",
    "GPT-4 Turbo with function calling + TypeScript + React Agent framework",
    "Gemini 1.5 Pro + Go + custom prompt engineering library",
    "Claude 3 Opus + chain-of-thought prompting + retry logic",
    "GPT-4o + tree-of-thoughts reasoning + Python asyncio",
    "OpenAI o1 preview + specialized logical reasoning mode",
    "Claude 3.5 + prompt chaining + parallel verification",
    "GPT-4 Turbo + semantic kernel + tool augmentation",
    "Claude Opus + XML structured prompting + validation",
    "Llama 3.1 405B + distributed inference + RAG",
    "Claude 3.5 + LangGraph + state machine reasoning",
    "GPT-4 + LlamaIndex + semantic chunking",
    "Gemini Pro 1.5 + 1M context window + full problem analysis",
    "Claude 3.5 + prompt caching + cost optimization",
    "GPT-4o + structured outputs + JSON schema enforcement",
]

TECH_STACKS_CASUAL = [
    "just vibing with ChatGPT tbh",
    "idk man i just ask it nicely",
    "copy paste from stackoverflow",
    "GPT-3.5 and prayers",
    "whatever's free tier lol",
    "claude but i dont really know what im doing",
    "gemini flash because im broke",
    "literally just hitting retry",
    "prompt engineering aka begging",
    "gpt4 when mom's credit card works",
    "running llama on my toaster",
    "microsoft copilot don't judge me",
    "chatgpt + vibes + manifestation",
    "temperature 2.0 chaos mode",
    "bing chat unironically",
    "asking my friend who codes",
]

TECH_STACKS_TROLLY = [
    "pure unfiltered copium",
    "thoughts and prayers algorithm",
    "magic 8 ball integration",
    "coin flip with extra steps",
    "my cat walks on keyboard",
    "stackoverflow blindly copied",
    "regex i found in 2003",
    "if it works dont touch it",
    "duct tape and hope",
    "works on my machine ¯\\_(ツ)_/¯",
    "legacy code from 1987",
    "i asked my dad",
    "outsourced to my dreams",
    "manifesting correct answers",
    "simply built different",
    "skill issue solver 9000",
]

# Some players don't bother with descriptions
NO_TECH_STACK = None

def create_realistic_stats():
    """Generate realistic win/loss stats with Gaussian distribution centered around 4 games"""
    # Gaussian distribution centered at 4, with std deviation of 4
    # This gives most users 0-8 games, with a long tail up to 25
    total = int(random.gauss(4, 4))
    
    # Clamp to 0-25 range
    total = max(0, min(25, total))
    
    # Determine skill level based on total games
    if total <= 5:
        skill_level = 'casual'
        win_rate = random.uniform(0.0, 0.6)  # Usually lose
    elif total <= 15:
        skill_level = 'regular'
        win_rate = random.uniform(0.3, 0.7)  # Mixed results
    else:  # 16-25 games
        skill_level = 'dedicated'
        win_rate = random.uniform(0.45, 0.75)  # Pretty good
    
    # Calculate wins, with cap at 17
    wins = int(total * win_rate)
    wins = min(wins, 17)  # Cap at 17 wins maximum
    
    losses = total - wins
    draws = 0
    
    return wins, losses, draws, total, skill_level

def choose_tech_stack(skill_level):
    """Choose appropriate tech stack based on skill level"""
    if skill_level == 'casual':
        # Casuals: 40% no description, 35% trolly, 20% casual, 5% serious
        choice = random.choices(
            ['none', 'trolly', 'casual', 'serious'],
            weights=[40, 35, 20, 5]
        )[0]
    elif skill_level == 'regular':
        # Regulars: 20% no description, 25% trolly, 40% casual, 15% serious
        choice = random.choices(
            ['none', 'trolly', 'casual', 'serious'],
            weights=[20, 25, 40, 15]
        )[0]
    else:  # dedicated (16-25 games)
        # Dedicated: 5% no description, 10% trolly, 30% casual, 55% serious
        choice = random.choices(
            ['none', 'trolly', 'casual', 'serious'],
            weights=[5, 10, 30, 55]
        )[0]
    
    if choice == 'none':
        return NO_TECH_STACK
    elif choice == 'trolly':
        return random.choice(TECH_STACKS_TROLLY)
    elif choice == 'casual':
        return random.choice(TECH_STACKS_CASUAL)
    else:
        return random.choice(TECH_STACKS_SERIOUS)

def seed_fake_users(num_users=50):
    """Seed the database with realistic fake users"""
    db = SessionLocal()
    
    try:
        # Check how many users already exist
        existing_count = db.query(User).count()
        print(f"📊 Current users in database: {existing_count}")
        
        # Shuffle to get random selection
        available_usernames = USERNAMES.copy()
        random.shuffle(available_usernames)
        
        created = 0
        skipped = 0
        
        for i in range(num_users):
            if i >= len(available_usernames):
                print("⚠️  Ran out of unique usernames")
                break
            
            username = available_usernames[i]
            
            # Check if user already exists
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                skipped += 1
                continue
            
            # Generate realistic stats
            wins, losses, draws, total_combats, skill_level = create_realistic_stats()
            
            # Choose tech stack based on skill level
            tech_desc = choose_tech_stack(skill_level)
            
            # Create user with realistic created_at (within last 6 months)
            days_ago = random.randint(1, 180)
            created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            user = User(
                username=username,
                password_hash=hash_password("demo_password_12345"),  # Not used for these accounts
                email=f"{username}@example.com",
                tech_description=tech_desc,
                wins=wins,
                losses=losses,
                draws=draws,
                total_combats=total_combats,
                created_at=created_at
            )
            
            db.add(user)
            created += 1
            
            # Print progress every 10 users
            if (created) % 10 == 0:
                print(f"✅ Created {created} users...")
        
        db.commit()
        
        print(f"\n🎉 Seeding complete!")
        print(f"   ✅ Created: {created} new users")
        print(f"   ⏭️  Skipped: {skipped} (already exist)")
        print(f"   📊 Total users now: {existing_count + created}")
        
        # Show some stats
        total_users = existing_count + created
        
        # Game count distribution
        casuals = db.query(User).filter(User.total_combats <= 5).count()
        regulars = db.query(User).filter(User.total_combats > 5, User.total_combats <= 15).count()
        dedicated = db.query(User).filter(User.total_combats > 15).count()
        
        print(f"\n🎮 Player activity distribution:")
        print(f"   🆕 Casuals (≤5 games): {casuals}")
        print(f"   🎯 Regulars (6-15 games): {regulars}")
        print(f"   💪 Dedicated (16-25 games): {dedicated}")
        
        # Rank tiers
        bronze = db.query(User).filter(User.wins < 10).count()
        silver = db.query(User).filter(User.wins >= 10, User.wins < 25).count()
        gold = db.query(User).filter(User.wins >= 25, User.wins < 50).count()
        diamond = db.query(User).filter(User.wins >= 50, User.wins < 100).count()
        pro = db.query(User).filter(User.wins >= 100).count()
        
        print(f"\n🏆 Rank distribution:")
        print(f"   🥉 Bronze: {bronze}")
        print(f"   🥈 Silver: {silver}")
        print(f"   🥇 Gold: {gold}")
        print(f"   💎 Diamond: {diamond}")
        print(f"   👑 Professional: {pro}")
        
        # Tech stack distribution
        with_tech = db.query(User).filter(User.tech_description.isnot(None)).count()
        without_tech = total_users - with_tech
        
        print(f"\n🛠️  Tech stack descriptions:")
        print(f"   ✍️  With description: {with_tech}")
        print(f"   ⏭️  No description: {without_tech}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    # Allow specifying number of users as command line arg
    num_users = 50
    if len(sys.argv) > 1:
        try:
            num_users = int(sys.argv[1])
        except ValueError:
            print("Usage: python seed_fake_users.py [number_of_users]")
            sys.exit(1)
    
    print(f"🌱 Seeding database with {num_users} fake users...")
    print()
    seed_fake_users(num_users)
