from langgraph.graph.state import CompiledStateGraph
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain.agents import create_agent

from validators import SelectNotificationSchema

from config import PERMANENT_FILES_STORE

from os.path import exists, join
from random import choice

from pandas import read_csv
from loguru import logger

@tool(
    'select_notification',
    args_schema=SelectNotificationSchema,
    description='''
        Select a notification template based on the student's solution, the correct task solution,
        and the already calculated evaluation score.

        The tool returns a notification template that must be adapted by the AI agent
        to the specific student solution and task.

        If no suitable notification exists, the tool returns an empty string.
        When the tool returns an empty string, the AI agent must generate the notification itself.
    '''
)
def select_notification(from_task: str, from_student: str, evaluate: float) -> str:
    logger.info('Launched \'select_notification\' tool')

    if evaluate == 1:
        status = 'success'

    elif 0 < evaluate < 1:
        status = 'warning'

    else:
        status = 'danger'

    notification_store = join(
        PERMANENT_FILES_STORE,
        'notifications.csv'
    )

    if not exists(notification_store):
        logger.warning('\'notifications.csv\' doesn\'t exist')
        return ''

    df = read_csv(notification_store)

    if df.empty:
        logger.warning('\'notifications.csv\' is empty')
        return ''

    notifications = df.iloc[:].values.tolist()

    target_notifications = [
        item[1]
        for item in notifications
        if item[0] == status
    ]

    if not target_notifications:
        logger.warning('\'target_notifications\' didn\'t find')
        return ''

    return choice(target_notifications)

TOOLS = [select_notification]

class InitAgentService:
    def __init__(
        self,
        template: str,
        base_url: str,
        model: str,
        temperature: float = 0.4
    ):
        self._system_message = SystemMessage(content=template)
        self._base_url = base_url
        self._model = model
        self._temperature = temperature

    def __call__(self) -> CompiledStateGraph:
        llm = ChatOllama(
            base_url=self._base_url,
            model=self._model,
            temperature=self._temperature
        )

        return create_agent(
            model=llm,
            tools=TOOLS,
            system_prompt=self._system_message
        )