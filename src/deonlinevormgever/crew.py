from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from deonlinevormgever.tools.custom_tool import BrandbookAnalysisTool, ToneOfVoiceTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Deonlinevormgever():
    """Deonlinevormgever crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def brandbook_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['brandbook_analyst'],
            verbose=True,
            tools=[BrandbookAnalysisTool()]
        )

    @agent
    def tone_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['tone_analyst'],
            verbose=True,
            tools=[ToneOfVoiceTool()]
        )

    @agent
    def prompt_composer(self) -> Agent:
        return Agent(
            config=self.agents_config['prompt_composer'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def analyze_brandbook(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_brandbook']
        )

    @task
    def analyze_tone(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_tone']
        )

    @task
    def build_prompt(self) -> Task:
        return Task(
            config=self.tasks_config['build_prompt'],
            output_file='design_prompt.json'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Deonlinevormgever crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
