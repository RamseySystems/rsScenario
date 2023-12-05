from rsScenarios import rsScenario
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(CURRENT_DIR, 'my_key_scenario_tool_gcp.json')

scenario = rsScenario.ScenarioTool("test", "sites.ramseysystems.co.uk")
scenario.list_projects()