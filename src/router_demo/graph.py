"""Graph assembly, routing by tier and escalation."""

from langgraph.graph import END, START, StateGraph

from router_demo.answering.nodes import make_answer_node, make_plan_node
from router_demo.answering.tiers import PLANNER, TIER_CONFIGS
from router_demo.llm.factory import make_llm
from router_demo.routing.classifier import classify
from router_demo.state import TIERS, RouterState, append_trace
from router_demo.validation.verdict import after_validation, validate

NEXT_TIER = {"simple": "medium", "medium": "complex", "complex": "complex"}


def build_models(settings):
    return {
        "classifier": make_llm(settings, "MODEL_SMALL", temperature=0),
        "simple": make_llm(settings, "MODEL_SMALL"),
        "medium": make_llm(settings, "MODEL_MEDIUM"),
        "complex": make_llm(settings, "MODEL_STRONG"),
        "planner": make_llm(settings, "MODEL_STRONG"),
        "judge": make_llm(settings, "MODEL_JUDGE", temperature=0),
    }


def route_by_tier(state):
    if state["tier"] == "complex":
        return "plan_complex"
    return "answer_" + state["tier"]


def escalate(state):
    verdict = state["verdict"]
    previous = state["tier"]
    issues = "; ".join(verdict["issues"])
    if not issues:
        issues = "Score " + str(verdict["score"]) + " below 7."
    trace = append_trace({"node": "escalate"}, state.get("trace"))
    return {"tier": NEXT_TIER[state["tier"]], "feedback": issues, "trace": trace}


def present(state):
    return {"trace": append_trace({"node": "present"}, state.get("trace"))}


def build_graph(models):
    graph = StateGraph(RouterState)
    graph.add_node("classify", lambda s: classify(s, models["classifier"]))
    graph.add_node("plan_complex", make_plan_node(PLANNER, models["planner"]))
    for tier in TIERS:
        graph.add_node(f"answer_{tier}", make_answer_node(TIER_CONFIGS[tier], models[tier]))
        graph.add_edge(f"answer_{tier}", "validate")
    graph.add_node("validate", lambda s: validate(s, models["judge"]))
    graph.add_node("escalate", escalate)
    graph.add_node("present", present)
    routes = ["answer_simple", "answer_medium", "plan_complex"]
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_by_tier, routes)
    graph.add_edge("plan_complex", "answer_complex")
    graph.add_conditional_edges("validate", after_validation, ["present", "escalate"])
    graph.add_conditional_edges("escalate", route_by_tier, routes)
    graph.add_edge("present", END)
    return graph.compile()
