# 简历筛选系统

一个基于规则匹配和LLM的智能简历筛选系统，支持多条件并发筛选，自动匹配岗位要求与简历信息。

## 项目结构

```
项目根目录/
├── core/                          # 核心功能模块
│   ├── __init__.py
│   ├── screener.py                # 主筛选器类 
│   ├── toolkit.py                 # 筛选工具箱 
│   └── models.py                  # 数据模型
│
├── filters/                       # 筛选器模块（按筛选条件分类）
│   ├── __init__.py
│   ├── base.py                    # 基础筛选器类（抽象基类）
│   ├── education.py               # 学历筛选
│   ├── major.py                   # 专业筛选
│   ├── age.py                     # 年龄筛选
│   ├── performance.py             # 绩效筛选
│   ├── title.py                   # 职称筛选
│   ├── work_experience.py         # 工作经历筛选
│   ├── work_years.py              # 工作经验筛选
│   └── political_status.py       # 政治面貌筛选
│
├── matchers/                      # 匹配器模块
│   ├── __init__.py
│   ├── rule_matcher.py            # 规则匹配器（所有规则匹配逻辑）
│   └── llm_matcher.py             # LLM匹配器（所有LLM匹配逻辑）
│
├── extractors/                    # 数据提取器模块
│   ├── __init__.py
│   ├── requirement_extractor.py   # 岗位要求提取器
│   └── resume_extractor.py        # 简历数据提取器
│
├── utils/                         # 工具模块
│   ├── __init__.py
│   ├── logger_config.py           # 日志配置模块
│   ├── major_library.py           # 专业库管理（加载、映射构建）
│   ├── calculator.py              # 计算工具（年龄、工作年限等）
│   └── data_loader.py             # 数据加载工具
│
├── managers/                      # 管理器模块
│   ├── __init__.py
│   └── llm_manager.py             # LLM模型管理器
│
├── exporters/                     # 导出模块
│   ├── __init__.py
│   └── result_exporter.py         # 结果导出器
│
├── data/                          # 数据目录
│   ├── 专业库.json                # 专业分类库
│   └── *.json                     # 岗位数据和简历数据
│
├── logs/                          # 日志目录
│   └── resume_filter.log          # 统一日志文件（所有模块日志集中输出）
│
├── config.py                      # 配置文件
├── resume_filter.py               # 主入口文件
└── requirements.txt               # 依赖文件
```

## 功能特性

- ✅ **多条件筛选**：支持学历、专业、年龄、绩效、职称、工作经历、工作经验、政治面貌等8个筛选维度
- ✅ **规则+LLM双重匹配**：优先使用规则匹配，复杂情况自动切换到LLM匹配
- ✅ **并发处理**：支持多岗位、多简历并发筛选，大幅提升处理效率
- ✅ **智能匹配**：自动匹配岗位名称与简历应聘岗位，只筛选相关简历
- ✅ **统一日志**：所有模块日志集中输出到单个文件，便于查看和调试
- ✅ **可配置日志级别**：支持控制台和文件分别设置日志级别

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置LLM服务

编辑 `config.py` 文件，配置LLM服务地址和模型：

```python
# LLM 配置
LLM_URL = "http://192.168.1.100:1234"  # LLM服务地址
LLM_MODEL = "qwen/qwen3-4b-2507"        # LLM模型名称
```

### 3. 配置日志级别（可选）

在 `config.py` 中配置日志级别：

```python
# 日志级别配置
# 可选值: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL_CONSOLE = "INFO"  # 控制台日志级别
LOG_LEVEL_FILE = "DEBUG"    # 文件日志级别（建议保持DEBUG以记录所有信息）
```

**日志级别说明：**
- `DEBUG`: 显示所有日志（最详细）
- `INFO`: 显示信息、警告、错误和严重错误
- `WARNING`: 显示警告、错误和严重错误
- `ERROR`: 只显示错误和严重错误
- `CRITICAL`: 只显示严重错误

### 4. 准备数据文件

将岗位数据和简历数据放在 `data/` 目录下：

- 岗位数据：JSON格式，包含岗位信息和资格条件
- 简历数据：JSON格式，包含简历基本信息和详细信息
- 专业库：`data/专业库.json`，用于专业匹配

## 使用方法

### 基本使用

1. **修改主入口文件**

编辑 `resume_filter.py`，修改数据文件路径：

```python
# 加载数据
jobs = load_job_data("./data/你的岗位数据.json")
resumes = load_resume_data("./data/你的简历数据.json")

# 专业库路径
major_library_path = "./data/专业库.json"
```

2. **运行程序**

```bash
python resume_filter.py
```

### 程序执行流程

1. **初始化**：加载LLM模型管理器（如果配置了LLM服务）
2. **数据加载**：加载岗位数据和简历数据
3. **岗位匹配**：自动匹配岗位名称与简历应聘岗位
4. **并发筛选**：对每个岗位的匹配简历进行并发筛选
5. **结果导出**：将筛选结果导出为JSON文件

### 筛选条件说明

系统支持以下8个筛选维度：

1. **学历要求**：匹配最高学历和全日制学历
2. **专业要求**：使用专业库进行专业匹配
3. **年龄要求**：计算年龄并匹配年龄限制
4. **绩效要求**：检查年度绩效情况
5. **职称要求**：匹配职称等级
6. **工作经历**：检查相关工作经历
7. **工作年限**：计算并匹配工作年限要求
8. **政治面貌**：匹配政治面貌要求

### 筛选结果

筛选结果包含：

- **简历ID**：简历序号
- **岗位ID**：岗位序号
- **岗位名称**：岗位名称
- **是否通过**：是否通过所有筛选条件
- **筛选详情**：每个筛选条件的详细结果
- **总结**：筛选结果总结

## 日志系统

### 日志文件

所有模块的日志统一输出到 `logs/resume_filter.log` 文件，便于集中查看和调试。

### 日志格式

- **文件日志**：`时间 - 模块名 - 级别 - 消息`
- **控制台日志**：`时间 - 级别 - 消息`（带颜色）

### 日志级别配置

在 `config.py` 中可以分别配置控制台和文件的日志级别：

```python
LOG_LEVEL_CONSOLE = "INFO"  # 控制台只显示INFO及以上级别
LOG_LEVEL_FILE = "DEBUG"    # 文件记录所有DEBUG及以上级别
```

## 开发说明

### 添加新的筛选条件

1. 在 `filters/` 目录下创建新的筛选器文件
2. 继承 `BaseFilter` 类
3. 实现 `filter` 方法
4. 在 `core/toolkit.py` 中添加对应的筛选方法
5. 在 `core/screener.py` 中调用新的筛选方法

### 添加新的匹配规则

1. 在 `matchers/rule_matcher.py` 中添加新的匹配方法
2. 在对应的筛选器中调用新的匹配方法

### 使用LLM匹配

当规则匹配无法处理复杂情况时，系统会自动切换到LLM匹配：

1. 在 `matchers/llm_matcher.py` 中添加LLM匹配方法
2. 在筛选器中调用LLM匹配方法

## 注意事项

1. **数据格式**：确保岗位数据和简历数据符合系统要求的JSON格式
2. **专业库**：专业匹配依赖专业库文件，确保 `data/专业库.json` 存在且格式正确
3. **LLM服务**：如果使用LLM匹配，确保LLM服务正常运行且可访问
4. **并发控制**：系统使用异步并发处理，注意系统资源使用情况
5. **日志文件**：日志文件会持续增长，定期清理或配置日志轮转