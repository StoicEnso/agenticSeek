#!/usr/bin/env python3

import os, sys
import uvicorn
import aiofiles
import configparser
import asyncio
import time
from typing import List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sources.llm_provider import Provider
from sources.agents import CasualAgent, CoderAgent, FileAgent, BrowserAgent, PlannerAgent
from sources.browser import Browser, create_driver
from sources.utility import pretty_print
from sources.logger import Logger
from sources.schemas import QueryRequest, QueryResponse

from dotenv import load_dotenv

load_dotenv()

api = FastAPI(title="AgenticSeek API", version="0.1.0")
logger = Logger("backend.log")
config = configparser.ConfigParser()
config.read('config.ini')

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists(".screenshots"):
    os.makedirs(".screenshots")
api.mount("/screenshots", StaticFiles(directory=".screenshots"), name="screenshots")

def initialize_system():
    stealth_mode = config.getboolean('BROWSER', 'stealth_mode')
    personality_folder = "jarvis" if config.getboolean('MAIN', 'jarvis_personality') else "base"
    languages = config["MAIN"]["languages"].split(' ')

    provider = Provider(
        provider_name=config["MAIN"]["provider_name"],
        model=config["MAIN"]["provider_model"],
        server_address=config["MAIN"]["provider_server_address"],
        is_local=config.getboolean('MAIN', 'is_local')
    )
    logger.info(f"Provider initialized: {provider.provider_name} ({provider.model})")

    # Try creating browser with our fixed approach
    browser = None
    try:
        logger.info("Initializing Chrome browser with fixed settings...")
        driver = create_driver(headless=False, stealth_mode=False)
        browser = Browser(driver, anticaptcha_manual_install=False)
        logger.info("Browser initialized successfully!")
    except Exception as e:
        logger.error(f"Browser initialization failed: {str(e)}")
        pretty_print("Browser initialization failed. Running in browser-less mode.", color="warning")
        browser = None

    # Create all agents
    agents = [
        CasualAgent(
            name=config["MAIN"]["agent_name"],
            prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
            provider=provider, verbose=False
        ),
        CoderAgent(
            name="coder",
            prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
            provider=provider, verbose=False
        ),
        FileAgent(
            name="File Agent",
            prompt_path=f"prompts/{personality_folder}/file_agent.txt",
            provider=provider, verbose=False
        )
    ]
    
    # Only add browser-dependent agents if browser was initialized
    if browser:
        agents.extend([
            BrowserAgent(
                name="Browser",
                prompt_path=f"prompts/{personality_folder}/browser_agent.txt",
                provider=provider, verbose=False, browser=browser
            ),
            PlannerAgent(
                name="Planner",
                prompt_path=f"prompts/{personality_folder}/planner_agent.txt",
                provider=provider, verbose=False, browser=browser
            )
        ])
    
    logger.info("Agents initialized")

    # Use simplified interaction without router
    class SimpleInteraction:
        def __init__(self, agents):
            self.agents = agents
            self.current_agent = agents[0] if agents else None
            self.last_query = None
            self.last_answer = None
            self.last_reasoning = None
            self.last_success = False
            self.is_active = True
            
        async def think(self):
            if not self.last_query:
                return False
                
            # Always use the first agent (casual agent)
            self.current_agent = self.agents[0]
            self.last_answer, self.last_reasoning = await self.current_agent.process(self.last_query, None)
            self.last_success = True if self.last_answer else False
            return self.last_success
            
        def get_last_blocks_result(self):
            if not self.current_agent:
                return []
            return self.current_agent.get_blocks_result()
            
        def speak_answer(self):
            # No-op
            pass
            
        def save_session(self):
            # No-op
            pass

    interaction = SimpleInteraction(agents)
    logger.info("Simple interaction initialized (router disabled)")
            
    return interaction

interaction = initialize_system()
is_generating = False
query_resp_history = []

@api.get("/screenshot")
async def get_screenshot():
    logger.info("Screenshot endpoint called")
    screenshot_path = ".screenshots/updated_screen.png"
    if os.path.exists(screenshot_path):
        return FileResponse(screenshot_path)
    logger.error("No screenshot available")
    return JSONResponse(
        status_code=404,
        content={"error": "No screenshot available"}
    )

@api.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy", "version": "0.1.0"}

@api.get("/is_active")
async def is_active():
    logger.info("Is active endpoint called")
    return {"is_active": interaction.is_active}

@api.get("/stop")
async def stop():
    logger.info("Stop endpoint called")
    if hasattr(interaction.current_agent, 'request_stop'):
        interaction.current_agent.request_stop()
    return JSONResponse(status_code=200, content={"status": "stopped"})

@api.get("/latest_answer")
async def get_latest_answer():
    global query_resp_history
    if interaction.current_agent is None:
        return JSONResponse(status_code=404, content={"error": "No agent available"})
    uid = str(uuid.uuid4())
    if not any(q["answer"] == interaction.current_agent.last_answer for q in query_resp_history):
        query_resp = {
            "done": "false",
            "answer": interaction.current_agent.last_answer,
            "reasoning": interaction.current_agent.last_reasoning,
            "agent_name": interaction.current_agent.agent_name if interaction.current_agent else "None",
            "success": interaction.current_agent.success if hasattr(interaction.current_agent, 'success') else False,
            "blocks": {f'{i}': block.jsonify() for i, block in enumerate(interaction.get_last_blocks_result())} if interaction.current_agent else {},
            "status": interaction.current_agent.get_status_message if hasattr(interaction.current_agent, 'get_status_message') else "No status available",
            "uid": uid
        }
        interaction.current_agent.last_answer = ""
        interaction.current_agent.last_reasoning = ""
        query_resp_history.append(query_resp)
        return JSONResponse(status_code=200, content=query_resp)
    if query_resp_history:
        return JSONResponse(status_code=200, content=query_resp_history[-1])
    return JSONResponse(status_code=404, content={"error": "No answer available"})

async def think_wrapper(interaction, query):
    try:
        interaction.last_query = query
        logger.info("Agents request is being processed")
        success = await interaction.think()
        if not success:
            interaction.last_answer = "Error: No answer from agent"
            interaction.last_reasoning = "Error: No reasoning from agent"
            interaction.last_success = False
        else:
            interaction.last_success = True
        pretty_print(interaction.last_answer)
        interaction.speak_answer()
        return success
    except Exception as e:
        logger.error(f"Error in think_wrapper: {str(e)}")
        interaction.last_answer = f""
        interaction.last_reasoning = f"Error: {str(e)}"
        interaction.last_success = False
        raise e

@api.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    global is_generating, query_resp_history
    logger.info(f"Processing query: {request.query}")
    query_resp = QueryResponse(
        done="false",
        answer="",
        reasoning="",
        agent_name="Unknown",
        success="false",
        blocks={},
        status="Ready",
        uid=str(uuid.uuid4())
    )
    if is_generating:
        logger.warning("Another query is being processed, please wait.")
        return JSONResponse(status_code=429, content=query_resp.jsonify())

    try:
        is_generating = True
        success = await think_wrapper(interaction, request.query)
        is_generating = False

        if not success:
            query_resp.answer = interaction.last_answer
            query_resp.reasoning = interaction.last_reasoning
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        if interaction.current_agent:
            blocks_json = {f'{i}': block.jsonify() for i, block in enumerate(interaction.current_agent.get_blocks_result())}
        else:
            logger.error("No current agent found")
            blocks_json = {}
            query_resp.answer = "Error: No current agent"
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        logger.info(f"Answer: {interaction.last_answer}")
        logger.info(f"Blocks: {blocks_json}")
        query_resp.done = "true"
        query_resp.answer = interaction.last_answer
        query_resp.reasoning = interaction.last_reasoning
        query_resp.agent_name = interaction.current_agent.agent_name
        query_resp.success = str(interaction.last_success)
        query_resp.blocks = blocks_json
        
        query_resp_dict = {
            "done": query_resp.done,
            "answer": query_resp.answer,
            "agent_name": query_resp.agent_name,
            "success": query_resp.success,
            "blocks": query_resp.blocks,
            "status": query_resp.status,
            "uid": query_resp.uid
        }
        query_resp_history.append(query_resp_dict)

        logger.info("Query processed successfully")
        return JSONResponse(status_code=200, content=query_resp.jsonify())
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Processing finished")
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()

if __name__ == "__main__":
    envport = os.getenv("BACKEND_PORT")
    if envport:
        port = int(envport)
    else:
        port = 8000
    uvicorn.run(api, host="0.0.0.0", port=port)