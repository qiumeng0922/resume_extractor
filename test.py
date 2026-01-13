# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser

# # 1. 定义提示词模板
# prompt = ChatPromptTemplate.from_template(
#     "今天{city}的天气是{weather}，请给用户一条穿衣建议。"
# )

# # 2. 使用 OpenAI 模型
# model = ChatOpenAI(
#     model="qwq-32b",  # 阿里云 DashScope 的模型名
#     api_key="sk-dff6d0f5d956485fa0ac71998e63d036",  # 替换为你的 DashScope API Key
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
# )

# # 3. 用 LCEL 拼接：输入 → 提示 → 模型 → 解析为字符串
# chain = prompt | model | StrOutputParser()

# # # 4. 调用（同步）
# # result = chain.invoke({"city": "北京", "weather": "晴，15°C"})
# # print(result)  # 输出："建议穿长袖衬衫加薄外套..."

# # 5. 流式输出（用户体验更好！）
# for chunk in chain.stream({"city": "上海", "weather": "雨，10°C"}):
#     print(chunk, end="", flush=True)

# test_self_rag_agent.py
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ===== 模拟检索器（替换成你的向量库）=====
def fake_retriever(query: str) -> List[str]:
    # 简单规则模拟：根据关键词返回“文档”
    if "巴黎" in query:
        return ["巴黎是法国首都，著名景点有埃菲尔铁塔、卢浮宫。"]
    elif "东京" in query:
        return ["东京是日本首都，以涩谷、浅草寺闻名。"]
    else:
        return ["未知地点信息。"]

# ===== LLM 设置 =====
llm = ChatOpenAI(
    model="qwen-max",  # 阿里云 DashScope 的模型名
    api_key="sk-dff6d0f5d956485fa0ac71998e63d036",  # 替换为你的 DashScope API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ===== 定义 Agent 状态 =====
class AgentState(TypedDict):
    query: str
    retrieved_docs: List[str]
    draft_answer: str
    reflection: str
    should_retry: bool
    final_answer: str
    retry_count: int

# ===== 节点函数 =====
def retrieve(state: AgentState):
    docs = fake_retriever(state["query"])
    return {"retrieved_docs": docs, "retry_count": state.get("retry_count", 0) + 1}

def generate_draft(state: AgentState):
    prompt = ChatPromptTemplate.from_template(
        "基于以下文档回答问题：\n\n文档：{docs}\n\n问题：{query}\n\n答案："
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"docs": "\n".join(state["retrieved_docs"]), "query": state["query"]})
    return {"draft_answer": answer}

def self_reflect(state: AgentState):
    reflect_prompt = ChatPromptTemplate.from_template(
        "你是一个严谨的助手。请评估以下答案是否可靠、是否完全基于提供的文档。\n\n"
        "问题：{query}\n"
        "文档：{docs}\n"
        "当前答案：{answer}\n\n"
        "请回答：这个答案是否可信？是否存在幻觉或信息不足？是否需要重新检索？\n"
        "仅回答 '需要重试' 或 '无需重试'。"
    )
    chain = reflect_prompt | llm | StrOutputParser()
    reflection = chain.invoke({
        "query": state["query"],
        "docs": "\n".join(state["retrieved_docs"]),
        "answer": state["draft_answer"]
    })
    should_retry = "需要重试" in reflection
    return {"reflection": reflection, "should_retry": should_retry}

def finalize(state: AgentState):
    return {"final_answer": state["draft_answer"]}

# ===== 条件路由函数 =====
def route_after_reflection(state: AgentState) -> Literal["retrieve", "finalize"]:
    if state["should_retry"] and state["retry_count"] < 2:
        return "retrieve"
    else:
        return "finalize"

# ===== 构建 LangGraph =====
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("generate_draft", generate_draft)
workflow.add_node("self_reflect", self_reflect)
workflow.add_node("finalize", finalize)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate_draft")
workflow.add_edge("generate_draft", "self_reflect")
workflow.add_conditional_edges("self_reflect", route_after_reflection)
workflow.add_edge("finalize", END)

app = workflow.compile()

# ===== 测试运行 =====
if __name__ == "__main__":
    import os
    os.environ["OPENAI_API_KEY"] = "sk-dff6d0f5d956485fa0ac71998e63d036"  # 替换为你的密钥

    inputs = {"query": "巴黎有哪些著名景点？"}
    result = app.invoke(inputs)
    print("\n✅ 最终答案：")
    print(result["final_answer"])
    print("\n🔍 反思记录：", result["reflection"])
    print("🔄 重试次数：", result["retry_count"])